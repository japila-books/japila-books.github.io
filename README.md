# The Internals Online Books

Welcome to ["The Internals Of" Online Books](https://github.com/japila-books) project! 🤙

I'm [Jacek Laskowski](https://pl.linkedin.com/in/jaceklaskowski), a Freelance Data(bricks) Engineer specializing in
[Apache Spark](https://books.japila.pl/apache-spark-internals/) (incl. [Spark SQL](https://books.japila.pl/spark-sql-internals/) and [Spark Structured Streaming](https://books.japila.pl/spark-structured-streaming-internals/)),
[Delta Lake](https://books.japila.pl/delta-lake-internals/),
[Databricks](https://www.databricks.com/),
and [Apache Kafka](https://books.japila.pl/kafka-internals/) (incl. [Kafka Streams](https://books.japila.pl/kafka-streams-internals/)) with brief forays into a wider data engineering space (e.g., [Trino](https://trino.io/), [Dask](https://www.dask.org/) and [dbt](https://www.getdbt.com/), mostly during [Warsaw Data Engineering](https://www.meetup.com/Warsaw-Data-Engineering/) meetups).

I'm very excited to have you here and hope you will enjoy exploring the internals of the open source projects together (in no particular order):

1. [Apache Spark](https://books.japila.pl/apache-spark-internals)
1. [Spark SQL](https://books.japila.pl/spark-sql-internals)
1. [Unity Catalog](https://books.japila.pl/unity-catalog-internals/)
1. [Spark Structured Streaming](https://books.japila.pl/spark-structured-streaming-internals/)
1. [Delta Lake](https://books.japila.pl/delta-lake-internals)
1. [Spark on Kubernetes](https://jaceklaskowski.github.io/spark-kubernetes-book/)
1. [PySpark](https://books.japila.pl/pyspark-internals)
1. [Apache Kafka](https://books.japila.pl/kafka-internals) (previously at [gitbooks.io](https://jaceklaskowski.gitbooks.io/apache-kafka/content/))
1. [Kafka Streams](https://books.japila.pl/kafka-streams-internals) (previously at [gitbooks.io](https://jaceklaskowski.gitbooks.io/mastering-kafka-streams/content/))
1. [ksqlDB](https://books.japila.pl/ksqldb-internals) (no longer maintained)
1. [Apache Beam](https://books.japila.pl/apache-beam-internals) (no longer maintained)
1. [Spark Standalone](https://books.japila.pl/spark-standalone-internals) (no longer maintained)

Please note that some books have less current content than others, but that's expected with a one-person project where so many things are truly interesting and thus time-consuming. Life's too short to taste everything :/

The aim of this project is to host all the current and future internals books under a single organization on GitHub and publish to a single domain via GitHub Pages (_until I find a better way to publish the books_).

## Custom Docker Image

The books projects use a custom Docker image.

The [official Docker image](https://squidfunk.github.io/mkdocs-material/getting-started/#with-docker-recommended) does not include all plugins the books need as well as is [no longer available](https://github.com/squidfunk/mkdocs-material/issues/2442).

See [build-image.sh](build-image.sh) shell script to learn more.

### Build Books Docker Image

Execute the [build-image.sh](build-image.sh) shell script to build the Docker image.

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

---

<a href="https://fosstodon.org/@jaceklaskowski" rel="me">Follow @jaceklaskowski on Mastodon!</a>
