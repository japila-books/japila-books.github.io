#!/usr/bin/env zsh

if [ "$#" -ne 1 ]; then
    echo "ERROR: INSIDERS_TAG not defined! Exiting..."
    exit
fi

INSIDERS_TAG=$1
print ">>> Building the books image with insiders tag: $INSIDERS_TAG"

# Aliases
oss () { cd ~/oss }
gco () { git checkout $1 }
books () { cd ~/books }

# FIXME Command-line option to trigger it
remove_all_images () {
  docker rmi -f $(docker image ls 'squidfunk/mkdocs-material-insiders:*' -q)
  docker rmi -f $(docker image ls 'jaceklaskowski/mkdocs-material-insiders:*' -q)
}

# Pull the given version of mkdocs-material-insiders
oss; cd mkdocs-material-insiders; git pull; gco $INSIDERS_TAG

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
  --build-arg INSIDERS_TAG=$INSIDERS_TAG \
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
