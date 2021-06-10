#!/usr/local/bin/zsh

if [ "$#" -ne 1 ]; then
    echo "ERROR: INSIDERS_TAG not defined! Exiting..."
    exit
fi

export INSIDERS_TAG=$1

# Aliases
oss () { cd ~/dev/oss }
gco () { git checkout $1 }
books () { cd ~/dev/books }
# FIXME Command-line option to trigger it
remove_all_images () {
  docker rmi -f $(docker image ls 'squidfunk/mkdocs-material-insiders:*' -q)
  docker rmi -f $(docker image ls 'jaceklaskowski/mkdocs-material-insiders:*' -q)
}

# In the repo directory, execute `docker build` as follows:
oss; cd mkdocs-material; git pull; gco $INSIDERS_TAG

# FIXME Command-line option to enable --no-cache
docker build \
  --no-cache \
  --tag squidfunk/mkdocs-material-insiders \
  --tag squidfunk/mkdocs-material-insiders:$INSIDERS_TAG \
  .

gco master

books; cd japila-books.github.io

docker build \
  --no-cache \
  --build-arg INSIDERS_TAG \
  --tag jaceklaskowski/mkdocs-material-insiders \
  --tag jaceklaskowski/mkdocs-material-insiders:$INSIDERS_TAG \
  .

# Clean Up

docker rmi \
  $(docker image ls 'squidfunk/mkdocs-material-insiders' \
      --filter=before=squidfunk/mkdocs-material-insiders:$INSIDERS_TAG -q)

docker rmi \
  $(docker image ls 'jaceklaskowski/mkdocs-material-insiders' \
      --filter=before=jaceklaskowski/mkdocs-material-insiders:latest -q)
