#!/bin/sh

DOCKER_NAME=cedricxie/l5kit
DOCKERFILE_NAME=Dockerfile_l5kit.gpu

docker build -t $DOCKER_NAME -f $DOCKERFILE_NAME . --no-cache