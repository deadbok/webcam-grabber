#!/bin/bash

function print_help() {
	echo "Convert all jpeg images in current directory to video"
	echo " First parameter: FPS"
	echo " Second parameter: Output video file name"
	exit 1
}

if [ -z "$1" ]
then
        print_help
fi

if [ -z "$2" ]
then
        print_help
fi

mencoder mf://*.jpg -mf fps=$1 -ovc lavc -lavcopts vcodec=mpeg4:mbd=1:vbitrate=12800:autoaspect=1 -o $2
