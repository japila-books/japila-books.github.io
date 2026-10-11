#!/usr/bin/env python3

"""Bump the version of the project a japila-books book is about (e.g. extra.uc.version,
extra.delta.version, extra.spark.version in mkdocs.yml) and, when given a local git
checkout of that project, sync the dependency versions in extra.* from it.

The book's mkdocs.yml is expected to follow the usual layout:

  extra:
    uc:                                    # the main project block
      version: 0.6.0
      github: https://github.com/unitycatalog/unitycatalog/blob/v0.6.0
    hadoop:                                # a dependency block
      # https://github.com/unitycatalog/unitycatalog/blob/v0.6.0/build.sbt#L40
      version: 3.4.2
      api: https://hadoop.apache.org/docs/r3.4.2/api/index.html
    spark:                                 # a dependency block with a deliberate pin
      # https://github.com/unitycatalog/unitycatalog/blob/v0.6.0/project/spark-versions.json#L6
      # version: 4.2.0
      version: 4.2.0

The main project block is the one with a version and a `github: .../blob/<ref>` URL
(use --key when there are several). Its GitHub repo is where the dependency source links
point to and where --latest looks for releases.

A dependency block is any block whose leading comment links to a file (and line) in the
main project's repo. For each, the script reads that line at the linked ref, turns it into
a pattern by replacing the old version with a capture group, and looks the pattern up in
the same file at the new tag. The new version, the new line number and the new tag are
written back, and every other field of the block that contains the old version (e.g. API
URLs) is updated too. A block with a "# version: X" comment keeps its active version as a
deliberate pin: the comment is updated and changing the pin is asked for.

When the inferred pattern isn't enough, an optional JSON config (default:
scripts/sync-version.json next to mkdocs.yml) can override it per block:

  {
    "tag": "v{version}",
    "deps": {
      "hibernate": {"derived": {"api": "https://docs.hibernate.org/orm/{major_minor}/javadocs"}},
      "kafka": {"pattern": "<kafka\\\\.version>([^<]+)<"},
      "spark": {"pick": "max"}
    }
  }

  tag      git tag of a version (default "v{version}")
  pattern  regex with one capture group for the version (default: inferred)
  file     file to search in the checkout (default: the one in the source link)
  pick     "first" (default) or "max" match of the pattern
  derived  field -> URL template; {version}, {major}, {minor}, {patch}, {major_minor}

Usage:
  sync-version.py NEW_VERSION [SRC_DIR] [--dry-run] [--key KEY] [--mkdocs PATH] [--config PATH]
  sync-version.py --latest [SRC_DIR] [...]

  NEW_VERSION  version of the main project to pin, e.g. 0.6.0 (a leading 'v' is stripped)
  SRC_DIR      Optional path to a local git checkout of the main project. When given, the
               script runs `git fetch --tags` there and reads the files at the new tag
               (`git show`, so the working tree is left untouched). A dependency that
               can't be synced is skipped (left unchanged), not fatal; see the status
               summary printed at the end.
               When omitted, only the main project's version (and fields derived from it)
               and the source links pointing to its old tag are updated.
  --latest     Fetch the latest release of the main project from GitHub and use it as
               NEW_VERSION, asking for confirmation first (in a terminal).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_CONFIG = Path("scripts") / "sync-version.json"

# A version as it appears in mkdocs.yml or a build file (also matches e.g. 6.5.0.Final)
VERSION_CHARS = r"""[^\s"'<>,;()\[\]]+"""

# The "github: https://github.com/<org>/<repo>/blob/<ref>" field of the main project block
GITHUB_BLOB_RE = re.compile(r"https://github\.com/([^/\s]+/[^/\s]+)/blob/([^/\s]+)")


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


def parse_version_tuple(v: str) -> tuple:
    # Non-numeric parts (e.g. "Final", "rc1") sort below numbers
    return tuple((1, int(p)) if p.isdigit() else (0, p) for p in re.split(r"[.\-]", v))


def version_parts(v: str) -> dict[str, str]:
    parts = v.split(".")
    return {
        "version": v,
        "major": parts[0],
        "minor": parts[1] if len(parts) > 1 else "",
        "patch": parts[2] if len(parts) > 2 else "",
        "major_minor": ".".join(parts[:2]),
    }


def version_re(v: str, strict: bool = False) -> re.Pattern:
    """Matches v as a whole version, not as part of a longer one (17 in se17 but not in 1.17
    or 175). With strict, v must not touch any word character either (17 in "17" only)."""
    before, after = (r"[\w.]", r"\w|\.\w") if strict else (r"[\d.]", r"\d|\.\d")
    return re.compile(rf"(?<!{before}){re.escape(v)}(?!{after})")


def run(cmd, cwd=None, check=True) -> str | None:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        if check:
            die(f"`{' '.join(cmd)}` failed:\n{result.stderr.strip()}")
        return None
    return result.stdout


# --- mkdocs.yml blocks ---------------------------------------------------------------

def _block_re(block_key: str) -> re.Pattern:
    # A block is the "  <key>:" line plus every following line indented >= 4 spaces
    # (its fields/comments) or blank; it stops at the next 2-space-indented key.
    return re.compile(r"^  " + re.escape(block_key) + r":\n(?:[ \t]{4,}.*\n|\n)*", re.MULTILINE)


def block_keys(text: str) -> list[str]:
    m = re.search(r"^extra:\n((?:[ \t].*\n|\n)*)", text, re.MULTILINE)
    if not m:
        die("could not find the 'extra' section in mkdocs.yml")
    return re.findall(r"^  (\w+):", m.group(1), re.MULTILINE)


def get_block(text: str, block_key: str) -> re.Match:
    m = _block_re(block_key).search(text)
    if not m:
        die(f"could not find 'extra.{block_key}' block in mkdocs.yml")
    return m


def get_block_field(text: str, block_key: str, field: str) -> str | None:
    fm = re.search(r"^    " + re.escape(field) + r":[ \t]*(.+?)[ \t]*$", get_block(text, block_key).group(0), re.MULTILINE)
    return fm.group(1) if fm else None


def block_fields(text: str, block_key: str) -> dict[str, str]:
    return dict(re.findall(r"^    (\w+):[ \t]*(.+?)[ \t]*$", get_block(text, block_key).group(0), re.MULTILINE))


def replace_block_field(text: str, block_key: str, field: str, new_value: str) -> str:
    m = get_block(text, block_key)
    block = m.group(0)
    fm = re.compile(r"^(    " + re.escape(field) + r":).*\n", re.MULTILINE).search(block)
    if not fm:
        die(f"could not find 'extra.{block_key}.{field}' in mkdocs.yml")
    new_block = block[: fm.start()] + f"{fm.group(1)} {new_value}\n" + block[fm.end():]
    return text[: m.start()] + new_block + text[m.end():]


def replace_in_block(text: str, block_key: str, old: str, new: str) -> str:
    m = get_block(text, block_key)
    return text[: m.start()] + m.group(0).replace(old, new) + text[m.end():]


def sync_derived_fields(text: str, block_key: str, old_version: str, new_version: str,
                        templates: dict[str, str]) -> str:
    """Updates the fields of a block derived from its version: those with a template, and
    every other field (but version) that contains the old version."""
    for field, value in block_fields(text, block_key).items():
        if field == "version":
            continue
        if field in templates:
            new_value = templates[field].format(**version_parts(new_version))
        else:
            new_value = version_re(old_version).sub(new_version, value)
        if new_value != value:
            text = replace_block_field(text, block_key, field, new_value)
    return text


# --- source links --------------------------------------------------------------------

def source_link_re(repo: str) -> re.Pattern:
    """Matches a "# https://github.com/<repo>/blob/<ref>/<path>#L<a>[-L<b>]" comment line,
    e.g. "# https://github.com/unitycatalog/unitycatalog/blob/v0.6.0/build.sbt#L362"."""
    return re.compile(
        r"^(    # https://github\.com/" + re.escape(repo) + r"/blob/)([^/\s]+)/(\S+?)#L(\d+)(?:-L(\d+))?[ \t]*$",
        re.MULTILINE,
    )


class SourceLink:
    def __init__(self, m: re.Match):
        self.prefix, self.ref, self.path = m.group(1), m.group(2), m.group(3)
        self.start = int(m.group(4))
        self.end = int(m.group(5)) if m.group(5) else None

    def render(self, ref: str, start: int) -> str:
        end = f"-L{self.end - self.start + start}" if self.end else ""
        return f"{self.prefix}{ref}/{self.path}#L{start}{end}"

    def lines(self) -> str:
        return f"L{self.start}" + (f"-L{self.end}" if self.end else "")


def find_source_link(text: str, block_key: str, repo: str) -> SourceLink | None:
    lm = source_link_re(repo).search(get_block(text, block_key).group(0))
    return SourceLink(lm) if lm else None


def replace_source_link(text: str, block_key: str, repo: str, new_link: str) -> str:
    m = get_block(text, block_key)
    new_block = source_link_re(repo).sub(lambda _: new_link, m.group(0), count=1)
    return text[: m.start()] + new_block + text[m.end():]


# --- source checkout -----------------------------------------------------------------

def git_show(src_dir: Path, ref: str, path: str) -> str | None:
    for rev in (ref, f"origin/{ref}"):
        out = run(["git", "show", f"{rev}:{path}"], cwd=src_dir, check=False)
        if out is not None:
            return out
    return None


def infer_pattern(old_text: str, link: SourceLink, old_version: str) -> str | None:
    """Turns the linked line(s) holding old_version into a regex with the version as the
    capture group, e.g. `<hadoop.version>3.4.2</hadoop.version>` into
    `<hadoop\\.version>(...)<`. The text after the version is kept only up to the closing
    delimiter, so a changing tail (e.g. a version-specific directory) doesn't break it."""
    lines = old_text.splitlines()
    for line in lines[link.start - 1: (link.end or link.start)]:
        vm = version_re(old_version, strict=True).search(line) or version_re(old_version).search(line)
        if not vm:
            continue
        before = line[: vm.start()].strip()
        after = re.match(r"""[^"'<>),;\]]*["'<>),;\]]?""", line[vm.end():]).group(0)

        def literal(s: str) -> str:
            return r"\s+".join(re.escape(p) for p in re.split(r"\s+", s))

        return literal(before) + f"({VERSION_CHARS})" + literal(after)
    return None


def find_version(pattern: str, text: str, pick: str) -> tuple[str, int, int] | tuple[None, None, int]:
    """Returns (value, 1-based line number, number of matches) of the first (or highest)
    match, or (None, None, 0)."""
    matches = list(re.finditer(pattern, text))
    if not matches:
        return None, None, 0
    m = max(matches, key=lambda m: parse_version_tuple(m.group(1))) if pick == "max" else matches[0]
    return m.group(1), text.count("\n", 0, m.start(1)) + 1, len(matches)


# --- latest release ------------------------------------------------------------------

def fetch_json(url: str):
    req = urllib.request.Request(
        url, headers={"User-Agent": "sync-version.py", "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def resolve_latest_version(repo: str, current_version: str, key: str) -> str:
    try:
        release = fetch_json(f"https://api.github.com/repos/{repo}/releases/latest")
        tag = release["tag_name"]
        print(f"latest {repo} release: {tag} ({release.get('name', '')})")
        print(f"published: {release.get('published_at', '?')}")
        print(f"url: {release.get('html_url', '')}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            die(f"GitHub API request for the latest release failed: {e.code} {e.reason}")
        # No GitHub releases (e.g. apache/spark): the highest vX.Y.Z tag then
        out = run(["git", "ls-remote", "--tags", "--refs", f"https://github.com/{repo}"])
        tags = re.findall(r"refs/tags/(v?\d+\.\d+\.\d+)$", out, re.MULTILINE)
        if not tags:
            die(f"no releases or vX.Y.Z tags found in {repo}")
        tag = max(tags, key=lambda t: parse_version_tuple(t.lstrip("v")))
        print(f"latest {repo} tag (no GitHub releases): {tag}")
    except urllib.error.URLError as e:
        die(f"could not reach the GitHub API: {e.reason}")

    latest_version = tag.lstrip("v")
    if latest_version == current_version:
        print(f"mkdocs.yml is already pinned to {current_version}")

    if sys.stdin.isatty():
        try:
            answer = input(f"Use {tag} as extra.{key}.version? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("aborted: no changes made")
            sys.exit(0)
    else:
        print(f"non-interactive: proceeding with {tag}")

    return latest_version


# --- main ----------------------------------------------------------------------------

def find_mkdocs_yml(arg: str | None) -> Path:
    if arg:
        path = Path(arg).expanduser().resolve()
        if not path.is_file():
            die(f"{path} not found")
        return path
    for d in (Path.cwd(), *Path.cwd().parents):
        if (d / "mkdocs.yml").is_file():
            return d / "mkdocs.yml"
    die("no mkdocs.yml in the current directory or its parents (use --mkdocs)")


def find_main_block(text: str, key: str | None) -> tuple[str, str, str]:
    """Returns (key, GitHub org/repo, ref) of the main project block."""
    candidates = []
    for k in block_keys(text):
        version, github = get_block_field(text, k, "version"), get_block_field(text, k, "github")
        gm = GITHUB_BLOB_RE.match(github or "")
        if version and gm and (key is None or k == key):
            candidates.append((k, gm.group(1), gm.group(2), version))
    if key and not candidates:
        die(f"'extra.{key}' needs a version and a 'github: https://github.com/<org>/<repo>/blob/<ref>' field")
    if len(candidates) > 1:
        # Prefer the block whose github URL points to its own version
        tagged = [c for c in candidates if c[2].lstrip("v") == c[3]]
        if len(tagged) == 1:
            candidates = tagged
        else:
            die(f"several main project candidates ({', '.join(c[0] for c in candidates)}): use --key")
    if not candidates:
        die("no extra.<key> block with a version and a 'github: .../blob/<ref>' field (use --key)")
    return candidates[0][:3]


def print_table(headers: list[str], rows: list[tuple[str, ...]]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)).rstrip()

    print(fmt_row(tuple(headers)))
    print(fmt_row(tuple("-" * w for w in widths)))
    for row in rows:
        print(fmt_row(row))


def ask_override_pin(key: str, current_pin: str, upstream: str, new_tag: str) -> bool:
    print(f"extra.{key}.version is pinned to {current_pin}; upstream {new_tag} uses {upstream}.")
    if not sys.stdin.isatty():
        return False
    try:
        answer = input(f"Override extra.{key}.version to {upstream}? [y/N] ").strip().lower()
    except EOFError:
        answer = ""
    return answer in ("y", "yes")


def sync_dependency(text: str, key: str, repo: str, src_dir: Path, new_tag: str,
                    dep_config: dict, file_cache: dict) -> tuple[str, str, str]:
    """Syncs extra.<key> from the source checkout. Returns (new_text, version_col, notes_col)."""
    link = find_source_link(text, key, repo)
    old_version = get_block_field(text, key, "version")
    if old_version is None:
        return text, "skipped", "no version field"
    # "# version: X" is the upstream value and the active version a deliberate pin
    upstream_m = re.search(r"^    # version:[ \t]*(\S+)", get_block(text, key).group(0), re.MULTILINE)
    old_upstream = upstream_m.group(1) if upstream_m else old_version

    def read(ref: str, path: str) -> str | None:
        if (ref, path) not in file_cache:
            file_cache[ref, path] = git_show(src_dir, ref, path)
        return file_cache[ref, path]

    path = dep_config.get("file", link.path)
    pattern = dep_config.get("pattern")
    if pattern is None:
        old_text = read(link.ref, link.path)
        if old_text is None:
            return text, "skipped", f"{link.path} not found at {link.ref}"
        pattern = infer_pattern(old_text, link, old_upstream)
        if pattern is None:
            return text, "skipped", f"{old_upstream} not on {link.path}#{link.lines()} at {link.ref} (set a pattern)"

    new_text = read(new_tag, path)
    if new_text is None:
        return text, "skipped", f"{path} not found at {new_tag}"
    new_version, line_no, match_count = find_version(pattern, new_text, dep_config.get("pick", "first"))
    if new_version is None:
        return text, "skipped", f"no match in {path} at {new_tag} (set a pattern)"

    text = replace_source_link(text, key, repo, link.render(new_tag, line_no))
    new_link = find_source_link(text, key, repo)
    line_col = f"{link.lines()} (unchanged)" if new_link.lines() == link.lines() else f"{link.lines()} -> {new_link.lines()}"
    if match_count > 1 and "pick" not in dep_config:
        line_col += f" (first of {match_count} matches; set pick)"

    if upstream_m:
        text = replace_in_block(text, key, upstream_m.group(0), f"    # version: {new_version}")
        if old_version == new_version:
            return text, f"unchanged ({old_version})", line_col
        if not ask_override_pin(key, old_version, new_version, new_tag):
            return text, f"kept at {old_version} (upstream {new_version})", line_col

    text = replace_block_field(text, key, "version", new_version)
    text = sync_derived_fields(text, key, old_version, new_version, dep_config.get("derived", {}))
    if old_version == new_version:
        return text, f"unchanged ({new_version})", line_col
    return text, f"{old_version} -> {new_version}", line_col


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("new_version", nargs="?", help="version of the main project to pin, e.g. 0.6.0")
    parser.add_argument("src_dir", nargs="?", help="path to a git checkout of the main project")
    parser.add_argument("--dry-run", action="store_true", help="print changes without writing mkdocs.yml")
    parser.add_argument("--latest", action="store_true",
                        help="fetch the latest release of the main project and use it as NEW_VERSION")
    parser.add_argument("--key", help="extra.<KEY> block of the main project (default: auto-detected)")
    parser.add_argument("--mkdocs", help="path to mkdocs.yml (default: found in the current directory or its parents)")
    parser.add_argument("--config", help=f"path to the JSON config (default: {DEFAULT_CONFIG} next to mkdocs.yml)")
    args = parser.parse_args()

    mkdocs_yml = find_mkdocs_yml(args.mkdocs)
    config_path = Path(args.config).expanduser() if args.config else mkdocs_yml.parent / DEFAULT_CONFIG
    if config_path.is_file():
        config = json.loads(config_path.read_text())
    elif args.config:
        die(f"{config_path} not found")
    else:
        config = {}
    deps_config = config.get("deps", {})
    tag_format = config.get("tag", "v{version}")

    original_text = mkdocs_yml.read_text()
    text = original_text
    main_key, repo, old_ref = find_main_block(text, args.key)
    old_version = get_block_field(text, main_key, "version")
    print(f"{mkdocs_yml}: extra.{main_key} ({repo})")

    if args.latest:
        # NEW_VERSION is supplied by --latest, so a lone leftover positional
        # (`--latest /path/to/src`) is SRC_DIR, not an explicit version.
        if args.new_version and args.src_dir:
            parser.error("pass either NEW_VERSION or --latest, not both")
        src_dir_arg = args.new_version
        new_version = resolve_latest_version(repo, old_version, main_key)
    else:
        if not args.new_version:
            parser.error("new_version is required unless --latest is given")
        new_version = args.new_version.lstrip("v")
        if not re.fullmatch(r"\d+(\.\d+)+([.\-]\w+)*", new_version):
            die(f"'{args.new_version}' doesn't look like a version (expected X.Y.Z)")
        src_dir_arg = args.src_dir
    new_tag = tag_format.format(version=new_version)

    # 1. Bump the main project's version and the fields derived from it (e.g. the github
    #    and docs URLs), then point every source link at its old tag to the new one.
    text = replace_block_field(text, main_key, "version", new_version)
    text = replace_in_block(text, main_key, f"/blob/{old_ref}", f"/blob/{new_tag}")
    text = sync_derived_fields(text, main_key, old_version, new_version, deps_config.get(main_key, {}).get("derived", {}))
    rows: list[tuple[str, str, str]] = [(
        f"{main_key}.version",
        "unchanged" if old_version == new_version else f"{old_version} -> {new_version}",
        repo,
    )]

    if not src_dir_arg:
        old_link = f"github.com/{repo}/blob/{old_ref}/"
        links = text.count(old_link)
        text = text.replace(old_link, f"github.com/{repo}/blob/{new_tag}/")
        rows.append(("source links", "", f"{links} {old_ref} link(s) -> {new_tag} (no source checkout given)"))
    else:
        # 2. Sync every block with a source link into the main project's repo
        src_dir = Path(src_dir_arg).expanduser().resolve()
        if not (src_dir / ".git").exists():
            die(f"{src_dir} is not a git checkout")
        print(f"fetching tags in {src_dir} ...")
        run(["git", "fetch", "--tags", "--quiet"], cwd=src_dir)
        if run(["git", "rev-parse", "--verify", "--quiet", f"{new_tag}^{{commit}}"], cwd=src_dir, check=False) is None:
            die(f"no {new_tag} in {src_dir}")

        file_cache: dict = {}
        for key in block_keys(text):
            if key == main_key or find_source_link(text, key, repo) is None:
                continue
            text, version_col, notes_col = sync_dependency(
                text, key, repo, src_dir, new_tag, deps_config.get(key, {}), file_cache
            )
            rows.append((f"{key}.version", version_col, notes_col))

    print()
    print("=== update status ===")
    print_table(["FIELD", "VERSION", "NOTES"], rows)

    if args.dry_run:
        print()
        print("--- dry run: mkdocs.yml not written ---")
        return
    if text == original_text:
        print()
        print("mkdocs.yml is up to date")
        return

    mkdocs_yml.write_text(text)
    print()
    print(f"updated {mkdocs_yml}")


if __name__ == "__main__":
    main()
