#!/bin/bash

SCRIPTDIR=$(realpath $(dirname $0))
PROJDIR=$(realpath $PWD)

function help(){
    echo "$0 is an helper script to build docker images"
    echo ""
    echo "Usage: $0 path-to-dockerfile"
    echo ""
    echo "- It launches the docker image build from the current directory and initialises 
    the variable dockerdir with the path to the Dockerfile"
    echo "- It creates an image with the name of the Dockerfile folder"
}

DOCKERFILE=""

while getopts "hf:" opt; do
  case ${opt} in
    h ) help
        exit -1
      ;;
    f ) DOCKERFILE=$OPTARG
      ;;
    * ) help
        exit -1
      ;;
  esac
done

if [[ ! -f $DOCKERFILE ]]; then
    echo "File $DOCKERFILE is not accessible"
    exit -1
fi

DOCKERDIR=$(dirname $DOCKERFILE)
IMGNAME=$(basename $DOCKERDIR)
cmd="docker build -t $IMGNAME --build-arg DOCKERDIR=$DOCKERDIR -f $DOCKERFILE ."

echo $cmd
$cmd
