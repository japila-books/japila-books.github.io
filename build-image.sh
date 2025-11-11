#!/usr/bin/env zsh

if [ "$#" -ne 1 ]; then
    echo "ERROR: TAG not defined! Exiting..."
    exit
fi

TAG=$1
print ">>> Building the books image with insiders tag: $TAG"

# Aliases
oss () { cd ~/oss }
gco () { git checkout $1 }
books () { cd ~/books }

# FIXME Command-line option to trigger it
remove_all_images () {
  docker rmi -f $(docker image ls 'squidfunk/mkdocs-material:*' -q)
  docker rmi -f $(docker image ls 'jaceklaskowski/mkdocs-material:*' -q)
}

# FIXME Command-line option to enable --no-cache
docker build \
  --no-cache \
  --build-arg TAG=$TAG \
  --tag jaceklaskowski/mkdocs-material \
  --tag jaceklaskowski/mkdocs-material:$TAG \
  .

# Clean Up

docker rmi \
  $(docker image ls 'squidfunk/mkdocs-material' \
      --filter=before=squidfunk/mkdocs-material:$TAG -q)

docker rmi \
  $(docker image ls 'jaceklaskowski/mkdocs-material' \
      --filter=before=jaceklaskowski/mkdocs-material:latest -q)
