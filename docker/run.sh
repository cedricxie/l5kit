#!/bin/sh

if [ "$1" = "" ]
then
    DOCKER_NAME=cedricxie/l5kit:latest
else
    DOCKER_NAME=cedricxie/l5kit:$1
fi

XSOCK=/tmp/.X11-unix
XAUTH=/home/$USER/.Xauthority
SHARED_DIR=/home/yxie/shared_dir
HOST_DIR=/home/$USER/shared_dir
SHARED_MEDIA_DIR=/media/yxie
HOST_MEDIA_DIR=/media/$USER

mkdir -p $HOST_DIR
echo "Shared directory: ${HOST_DIR}"

docker run \
    -it --rm \
    --volume=$HOST_DIR:$SHARED_DIR:rw \
    --volume=$HOST_MEDIA_DIR:$SHARED_MEDIA_DIR:rw \
    --volume=$XSOCK:$XSOCK:rw \
    --volume=$XAUTH:$XAUTH:rw \
    --env="XAUTHORITY=${XAUTH}" \
    --env="DISPLAY=${DISPLAY}" \
    --env="QT_X11_NO_MITSHM=1" \
    -u yxie \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /dev/video0:/dev/video0 \
    --net=host \
    --ipc=host \
    --gpus=all \
    $DOCKER_NAME