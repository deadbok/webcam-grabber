#!/bin/bash

function print_help() {
	echo "Grab images from an URL"
	echo " First parameter: the interval in seconds"
	echo " Second parameter: the URL from where to grab the image"
	echo " Third parameter: the directory to save the files"
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


while true;
do
	NOW=$(date +"%Y-%m-%d-%H-%M")
	sleep $1
	echo "Getting ";
	wget $2 -O $3/$NOW.jpg;
done
