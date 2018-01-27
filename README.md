# Webcam grabber

Small utility made for a friend, to grab images from a webcam off the web at
a specific interval and convert these into a time-laspe video.

## Features

* Grab preview image at given intervals

## grab_cam.py

This shell script grabs an image from an URL using wget at regular intervals.
Most webcam accessible through a webpage has an url for a preview that is updated
regularly, this is what is downloaded using this script.

### Command line

grab_cam.py *interval* *url* *target_directory* *light_level*

* *interval*: the interval in seconds (default: 60)
* *url*: the URL from where to grab the image
* *target_directory*: the directory to save the files
* *light_level*: Average B/W light level in percentage. Images below this 
  threshold are skipped.

## to_video.sh

Convert all jpeg images in current directory to video.

 to_video.sh *fps* *output_filename*

* *fps*: FPS of the video
* *output_filename*: Output video file name

## Dependecies

* tqdm
* PIL
* mencoder
