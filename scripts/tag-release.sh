#!/usr/bin/env bash
# Creates and pushes a git tag matching the version of the project a book is about
# (e.g., extra.spark.version in mkdocs.yml).
set -euo pipefail

remote=origin

usage() {
  cat <<EOF
usage: $(basename "$0") [--key KEY] [--yes] [--help]

Creates a git tag matching the version of the project the book is about and pushes it
to $remote. Execute it in the book project (mkdocs.yml is looked up in the current
directory and its parents).

The project is the extra.<KEY> block in mkdocs.yml with a version and a
'github: https://github.com/<org>/<repo>/blob/<ref>' field (e.g., extra.spark,
extra.delta, extra.uc).

  -k, --key KEY  use extra.KEY.version (default: auto-detected)
  -y, --yes      skip the confirmation prompt
  -h, --help     show this help and exit
EOF
}

yes=false
key=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y) yes=true ;;
    --key|-k)
      [[ $# -ge 2 ]] || { usage >&2; exit 1; }
      key="$2"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if ! command -v yq &>/dev/null; then
  echo "error: yq is required (https://github.com/mikefarah/yq)" >&2
  exit 1
fi

dir="$PWD"
until [[ -f "$dir/mkdocs.yml" ]]; do
  if [[ "$dir" == "/" ]]; then
    echo "error: no mkdocs.yml in $PWD or its parents" >&2
    exit 1
  fi
  dir="$(dirname "$dir")"
done
cd "$dir"

if [[ -z "$key" ]]; then
  keys=$(yq '.extra | to_entries | .[] | select((.value | tag) == "!!map" and .value.version != null and ((.value.github // "") | test("^https://github\.com/[^/]+/[^/]+/blob/"))) | .key' mkdocs.yml)
  if [[ -z "$keys" ]]; then
    echo "error: no extra.<key> with a version and a 'github: .../blob/<ref>' field in $dir/mkdocs.yml (use --key)" >&2
    exit 1
  fi
  if [[ $(wc -l <<<"$keys") -gt 1 ]]; then
    echo "error: several candidates in $dir/mkdocs.yml ($(paste -sd ' ' - <<<"$keys")): use --key" >&2
    exit 1
  fi
  key="$keys"
fi

version=$(KEY="$key" yq '.extra[strenv(KEY)].version' mkdocs.yml)
if [[ "$version" == "null" ]]; then
  echo "error: no extra.$key.version in $dir/mkdocs.yml" >&2
  exit 1
fi
tag="v${version}"

if git rev-parse "$tag" &>/dev/null; then
  echo "error: tag $tag already exists" >&2
  exit 1
fi

if [[ "$yes" != true ]]; then
  read -r -p "Create and push tag $tag (extra.$key.version) at $(git rev-parse --short HEAD) to $remote? [y/N] " reply
  case "$reply" in
    [yY]|[yY][eE][sS]) ;;
    *)
      echo "aborted"
      exit 1
      ;;
  esac
fi

git tag "$tag"
echo "created tag $tag"

git push "$remote" "$tag"
echo "pushed tag $tag to $remote"
