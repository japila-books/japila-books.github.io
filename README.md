# The Internals Online Books

Welcome to ["The Internals Of" Online Books](https://github.com/japila-books) project! 🤙

I'm [Jacek Laskowski](https://pl.linkedin.com/in/jaceklaskowski), an IT freelancer specializing in [Apache Spark](https://spark.apache.org/), [Delta Lake](https://delta.io/) and [Apache Kafka](https://kafka.apache.org/) (with brief forays into a wider data engineering space, e.g. [Trino](https://trino.io/) and [ksqlDB](https://ksqldb.io/), mostly during [Warsaw Data Engineering](https://www.meetup.com/Warsaw-Data-Engineering/) meetups).

I'm very excited to have you here and hope you will enjoy exploring the internals of the open source projects together (in no particular order):

1. [Apache Spark](https://books.japila.pl/apache-spark-internals)
1. [Spark SQL](https://jaceklaskowski.github.io/mastering-spark-sql-book/)
1. [Spark Structured Streaming](https://jaceklaskowski.github.io/spark-structured-streaming-book/)
1. [Delta Lake](https://books.japila.pl/delta-lake-internals)
1. [Spark on Kubernetes](https://jaceklaskowski.github.io/spark-kubernetes-book/)
1. [PySpark](https://books.japila.pl/pyspark-internals)
1. [Apache Kafka](https://jaceklaskowski.gitbooks.io/apache-kafka/content/)
1. [Kafka Streams](https://jaceklaskowski.gitbooks.io/mastering-kafka-streams/content/)
1. [Apache Beam](https://books.japila.pl/apache-beam-internals)

Please note that some books have less current content than others, but that's expected with a one-person project where some many things are so interesting and thus time-consuming. Life's too short to taste everything :/

The aim of this project is to host all the current and future internals books under a single organization on GitHub and publish to a single domain via GitHub Pages (_until I find a better way to publish the books_).

## Custom Docker Image

The books projects use a custom Docker image.

The [official Docker image](https://squidfunk.github.io/mkdocs-material/getting-started/#with-docker-recommended) does not include all plugins the books need as well as is [no longer available](https://github.com/squidfunk/mkdocs-material/issues/2442).

Review [Dockerfile](Dockerfile) and [requirements.txt](requirements.txt) files to learn more.

### Build Books Docker Image

```shell
export INSIDERS_TAG=7.1.3-insiders-2.6.0
```

Clone the [Material for MkDocs Insiders](https://squidfunk.github.io/mkdocs-material/insiders/) repo and execute the following command inside:

```shell
docker build \
  --tag squidfunk/mkdocs-material-insiders \
  --tag squidfunk/mkdocs-material-insiders:$INSIDERS_TAG \
  .
```

Switch back to this repo and execute the following command:

```shell
docker build \
  --build-arg INSIDERS_TAG \
  --tag jaceklaskowski/mkdocs-material-insiders \
  --tag jaceklaskowski/mkdocs-material-insiders:$INSIDERS_TAG \
  .
```

You may want to delete all the earlier images (to clean up space). Pardon such convoluted commands.

```shell
docker rmi \
  $(docker image ls 'ghcr.io/squidfunk/mkdocs-material-insiders' \
      --filter=before=ghcr.io/squidfunk/mkdocs-material-insiders:$INSIDERS_TAG -q)
```

```shell
docker rmi \
  $(docker image ls 'jaceklaskowski/mkdocs-material-insiders' \
      --filter=before=$(docker image ls 'jaceklaskowski/mkdocs-material-insiders:latest' -q) -q)
```

**NOTE** Learn more about `docker build` command in the [official documentation of Docker](https://docs.docker.com/engine/reference/commandline/build/).

### Build Book

Use `docker run` command with `build` argument to build a book.

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  jaceklaskowski/mkdocs-material-insiders \
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
  jaceklaskowski/mkdocs-material-insiders \
  serve --dirtyreload --verbose --dev-addr 0.0.0.0:8000
```

### List Outdated Packages

Run an interactive shell in a container.

```text
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  --entrypoint sh \
  jaceklaskowski/mkdocs-material-insiders
```

While inside, execute the following command to list outdated packages, and show the latest version available (as described [here](https://pip.pypa.io/en/stable/user_guide/#listing-packages)).

```text
python -m pip list --outdated
```
