# The Internals Online Books

Welcome to ["The Internals Of" Online Books](https://books.japila.pl/) project! 🤙

I'm [Jacek Laskowski](https://pl.linkedin.com/in/jaceklaskowski), a Freelance Data Engineer 🧱
specializing in
[Apache Spark](https://books.japila.pl/apache-spark-internals/) (incl. [Spark SQL](https://books.japila.pl/spark-sql-internals/) and [Spark Structured Streaming](https://books.japila.pl/spark-structured-streaming-internals/)),
[Delta Lake](https://books.japila.pl/delta-lake-internals/),
[Unity Catalog](https://books.japila.pl/unity-catalog-internals/),
[MLflow](https://mlflow.org/ambassadors),
[DSPy](https://dspy.ai),
[Databricks](https://github.com/jaceklaskowski/learn-databricks)
with brief forays into a wider Data, ML and AI Engineering space (mostly during [Warsaw Data Engineering](https://www.meetup.com/Warsaw-Data-Engineering/) meetups).

I'm very excited to have you here and hope you will enjoy exploring the internals of the open source projects together (in no particular order):

1. [Apache Spark](https://books.japila.pl/apache-spark-internals)
1. [Spark Declarative Pipelines](https://books.japila.pl/spark-declarative-pipelines)
1. [Spark SQL](https://books.japila.pl/spark-sql-internals)
1. [Unity Catalog](https://books.japila.pl/unity-catalog-internals/)
1. [Spark Connect](https://books.japila.pl/spark-connect-internals)
1. [Spark Structured Streaming](https://books.japila.pl/spark-structured-streaming-internals/)
1. [Delta Lake](https://books.japila.pl/delta-lake-internals)
1. [Spark on Kubernetes](https://jaceklaskowski.github.io/spark-kubernetes-book/)
1. [PySpark](https://books.japila.pl/pyspark-internals)
1. [Apache Kafka](https://books.japila.pl/kafka-internals)
1. [Kafka Streams](https://books.japila.pl/kafka-streams-internals)

Please note that some books have less current content than others, but that's expected with a one-person project where so many things are truly interesting and thus time-consuming. Life's too short to taste everything :/

The aim of this project is to host all the current and future internals books under a single organization on GitHub and publish to a single domain via GitHub Pages (_until I find a better way to publish the books_).

## Custom Docker Image

The japila-books project uses [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) documentation framework.

The book projects use a custom Docker image.

Use [build-image.sh](build-image.sh) shell script to build the custom Docker image.

### Build Books Docker Image

Start [Colima](https://github.com/abiosoft/colima).

```bash
colima start
```

Execute the [build-image.sh](build-image.sh) shell script to build the Docker image.

```bash
./build-image.sh [version_tag]
```

Go to <https://github.com/squidfunk/mkdocs-material/tags> to find the available insiders tags.

## Build Book

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  jaceklaskowski/mkdocs-material \
  build --clean
```

**TIP:** Consult the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/creating-your-site/) documentation to get started.

### Live Editing

Use `docker run` command with `serve` argument (with `--dirtyreload` for faster reloads) in the project root (the folder with [mkdocs.yml](mkdocs.yml)).

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  jaceklaskowski/mkdocs-material \
  serve --dirtyreload --verbose --dev-addr 0.0.0.0:8000
```

### List Outdated Packages

Run an interactive shell in a container.

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  --entrypoint sh \
  jaceklaskowski/mkdocs-material
```

While inside, execute the following command to list outdated packages, and show the latest version available (as described [here](https://pip.pypa.io/en/stable/user_guide/#listing-packages)).

```shell
pip list --outdated
```

## Sync Versions

Use [scripts/sync-version.py](scripts/sync-version.py) to bump the version of the project a book is about (e.g., `extra.spark.version` in `mkdocs.yml`) and sync the dependency versions (`extra.*`) from a local git checkout of that project.

Execute the script in the book project root (the folder with `mkdocs.yml`).

```shell
../japila-books.github.io/scripts/sync-version.py v4.2.0 ~/oss/spark
```

Use `--dry-run` to print the changes without writing `mkdocs.yml`, and `--latest` (in place of the version) to use the latest release of the project.

```shell
../japila-books.github.io/scripts/sync-version.py --latest ~/oss/spark --dry-run
```

A book can fine-tune the sync with an optional `scripts/sync-version.json` config (e.g., to pick the highest of several matching versions or to build URLs from a version). Use `--help` for the details.

## Tag Release

Use [scripts/tag-release.sh](scripts/tag-release.sh) to create a git tag matching the version of the project a book is about (e.g., `extra.spark.version` in `mkdocs.yml`) and push it to `origin`.

Execute the script in the book project (`mkdocs.yml` is looked up in the current directory and its parents).

```shell
../japila-books.github.io/scripts/tag-release.sh
```

The project is auto-detected as the `extra.<key>` block in `mkdocs.yml` with a `version` and a `github: https://github.com/<org>/<repo>/blob/<ref>` field (e.g., `extra.spark`, `extra.delta`, `extra.uc`). Use `--key` to pick one explicitly and `--yes` to skip the confirmation prompt.

```shell
../japila-books.github.io/scripts/tag-release.sh --key spark --yes
```

The script requires [yq](https://github.com/mikefarah/yq).
