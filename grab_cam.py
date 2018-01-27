#!/bin/env python3
"""
Grab an image off the internet at regular intervals.
"""
import argparse
import os
import time
import requests
from tqdm import tqdm
from PIL import Image


def image_diff(ffilename, sfilename):
    """
    Caompare images.

    :param ffilename: File name of the first image.
    :param sfilename: File name of the second image.
    :return: True if different.
    """
    fimage = Image.open(ffilename)
    simage = Image.open(sfilename)

    fpixels = list(fimage.getdata())
    spixels = list(simage.getdata())

    for pixel in range(0, len(fpixels)):
        if spixels[pixel] != fpixels[pixel]:
            return True

    return False


def image_average(filename):
    """
    Calculate the avrage B/W light level.

    :param filename: Image file name
    :return: the avarage B/W saturation of the picture in percent
    """
    image = Image.open(filename)

    pixels = list(image.getdata())

    avg = 0
    npixels = 0

    for pixel in pixels:
        avg += (pixel[0] + pixel[1] + pixel[2]) / 3
        npixels += 1

    avg /= npixels
    return avg / 256 * 100


def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int,
                        help='Interval betewwn grabs, in secends', default=60)
    parser.add_argument('url', type=str, help='URL of the image')
    parser.add_argument('target_dir', type=str, help='Target directory')
    parser.add_argument('light_percent', type=int,
                        help="Image are discarded below this B/W light level in percen", default=0)
    args = parser.parse_args()

    print("Interval:\t\t{}".format(args.interval))
    print("URL:\t\t\t{}".format(args.url))
    print("Directory:\t\t{}".format(args.target_dir))
    print("Light level in %:\t{}".format(args.light_percent))

    lastimage = None
    retries = 0

    while True:
        now = time.strftime('%Y-%m-%d-%H-%M-%S')
        target_name = "{}/{}.jpg".format(args.target_dir, now)
        remove = False

        print("Grabbing: {}".format(target_name))
        response = requests.get(args.url, stream=True)
        with open(target_name, "wb") as target:
            for data in tqdm(response.iter_content()):
                target.write(data)

        interval = args.interval
        if lastimage is not None:
            if image_diff(lastimage, target_name) is False:
                print("Images are the same, backing off a bit.")
                remove = True
                interval = 10
                retries += 1
                if retries > 5:
                    print("Images keep being the same, skipping.")
                    interval = args.interval
                    retries = 0
            else:
                retries = 0

        light_percent = image_average(target_name)
        print("Average percantage of the maximum " +
              "B/W value: {:.2f}".format(light_percent))
        if light_percent < args.light_percent:
            print("Image is to dark ({:.0f}/{}), skipping".format(light_percent,
                                                                  args.light_percent))
            remove = True

        if remove:
            os.remove(target_name)
        else:
            lastimage = target_name

        time.sleep(interval)


if __name__ == "__main__":
    main()
