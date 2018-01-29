#!/bin/bash

function print_help() {
	echo "Convert all jpeg images in current directory to video"
	echo
	echo "$0 fps output_filename"
	echo " fps: FPS of the video"
	echo " ext: input file extension"
	echo " output_filename: Output video file name"
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

if [ -z "$3" ]
then
        print_help
fi

mencoder "mf://*.$2" -mf fps="$1" -ovc lavc -lavcopts vcodec=mpeg4:mbd=1:vbitrate=12800:autoaspect=1 -o "$3"
