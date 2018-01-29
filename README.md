# Webcam grabber

Small utility made for a friend, to grab images from a webcam off the web at
a specific interval and convert these into a time-laspe video.

## Features

* Grab preview image at given intervals
    * Detect and skip similar images
    * Detect and skip dark images
    * Honour daylight time using https://sunrise-sunset.org/
* Script to convert all images to video

## grab_cam.py

This shell script grabs an image from an URL using wget at regular intervals.
Most webcam accessible through a webpage has an url for a preview that is updated
regularly, this is what is downloaded using this script.

### Command line

    usage: grab_cam.py [-h] [-l, --light LIGHT_PERCENT]
                    [-d, --daylight DAYLIGHT DAYLIGHT]
                    interval url target_dir

    positional arguments:
    interval              Interval betewwn grabs, in secends
    url                   URL of the image
    target_dir            Target directory

    optional arguments:
    -h, --help            show this help message and exit
    -l, --light LIGHT_PERCENT
                            Image are discarded below this B/W light level in
                            percent
    -d, --daylight DAYLIGHT DAYLIGHT
                            Longetude and latitude to only grab during
                            astronomical daylight hours


## to_video.sh

Convert all jpeg images in current directory to video.

 to_video.sh *fps* *extension* *output_filename*

* *fps*: FPS of the video
* *extension*: Input image extension
* *output_filename*: Output video file name

## Dependecies

### Grabber

* Pillow
* BeautifulSoup

#### Installing (Debian like systems)

As root do:

    apt-get install python3-bs4 python3-pil

### Video converter

* mencoder

#### Installing (Debian like systems)

As root do:

    apt-get install mencoder 
