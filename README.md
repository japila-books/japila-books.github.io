# The Internals Online Books

Welcome to ["The Internals Of" Online Books](https://github.com/japila-books) project! 🤙

I'm [Jacek Laskowski](https://pl.linkedin.com/in/jaceklaskowski), a Freelance Data Engineer 🧱
specializing in
[Apache Spark](https://books.japila.pl/apache-spark-internals/) (incl. [Spark SQL](https://books.japila.pl/spark-sql-internals/) and [Spark Structured Streaming](https://books.japila.pl/spark-structured-streaming-internals/)),
[Delta Lake](https://books.japila.pl/delta-lake-internals/),
[Unity Catalog](https://books.japila.pl/unity-catalog-internals/),
[MLflow](https://mlflow.org/),
[DSPy](https://dspy.ai/),
[Databricks](https://github.com/jaceklaskowski/learn-databricks)
with brief forays into a wider data engineering space (mostly during [Warsaw Data Engineering](https://www.meetup.com/Warsaw-Data-Engineering/) meetups).

I'm very excited to have you here and hope you will enjoy exploring the internals of the open source projects together (in no particular order):

1. [Apache Spark](https://books.japila.pl/apache-spark-internals)
1. [Spark SQL](https://books.japila.pl/spark-sql-internals)
1. [Unity Catalog](https://books.japila.pl/unity-catalog-internals/)
1. [Spark Connect](https://books.japila.pl/spark-connect-internals)
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

## Custom Books Docker Image

The japila-books project uses [Zensical](https://zensical.org/) documentation framework.

The book projects use a custom Docker image to install extra plugins.

Use [build-image.sh](build-image.sh) shell script to build the custom Docker image.

### Build Image

Start [Colima](https://github.com/abiosoft/colima).

```bash
colima start
```

Execute the [build-image.sh](build-image.sh) shell script to build the Docker image.

```bash
./build-image.sh
```

## Build Book

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  jaceklaskowski/zensical \
  build --clean
```

## Live Editing

Use `docker run` command in the project root (the folder with [zensical.yml](zensical.yml)).

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  jaceklaskowski/zensical
```

## List Outdated Packages

Run an interactive shell in a container.

```shell
docker run \
  --rm \
  -it \
  -p 8000:8000 \
  -v ${PWD}:/docs \
  --entrypoint sh \
  jaceklaskowski/zensical
```

While inside, execute the following command to list outdated packages, and show the latest version available (as described [here](https://pip.pypa.io/en/stable/user_guide/#listing-packages)).

```shell
pip list --outdated
```
