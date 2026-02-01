#!/usr/bin/env zsh

# Parse command-line arguments
if [[ "$1" == "-l" || "$1" == "--list" ]]; then
  print ">>> Available squidfunk/mkdocs-material images:"
  docker image ls squidfunk/mkdocs-material
  exit 0
fi

if [[ -z "$1" ]]; then
  print "Error: TAG is required"
  print "Usage: $0 <tag>"
  print "       $0 -l|--list    List available squidfunk/mkdocs-material images"
  exit 1
fi

TAG=$1

print ">>> Building the books image with tag: $TAG"

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

print "Cleaning up"

docker rmi \
  $(docker image ls 'squidfunk/mkdocs-material' \
      --filter=before=squidfunk/mkdocs-material:$TAG -q)

docker rmi \
  $(docker image ls 'jaceklaskowski/mkdocs-material' \
      --filter=before=jaceklaskowski/mkdocs-material:latest -q)
