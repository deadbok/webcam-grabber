#!/bin/env python3
"""
Grab an image off the internet at regular intervals.
"""
import argparse
import datetime
import json
import logging
import threading
from io import BytesIO
import time
import timeit
import requests
from PIL import Image


logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(message)s')


class Webcam(object):
    """
    Class to download webcam image from an URL
    """
    SAVED = 0
    TOO_DARK = 1
    SAME = 3
    NIGHT = 4

    def __init__(self):
        """
        Constructor
        """
        self.image = None

    def grab(self, last_filename, filename, avg=0, url=None):
        """
        Helper method that grabs the image and check its light level
        and compares it to the last image.

        :param last_filename: File name of the last image
        :param filename: File name to save the new image to
        :param avg: Avarage light level floor
        :param url: Url of the webcam preview image.
        :return: Webcam.SAVED, Webcam.TOO_DARK, Webcam.SAME, and Webcam.NIGHT
        """
        self.image = None
        self.grab_image(url)

        logging.debug("Last image:\t\t%s", last_filename)

        if last_filename is None:
            # No last image
            if self.image_average() >= avg:
                # Light is okay, save
                logging.info("Saving:\t\t\t%s", filename)
                self.image.save(filename, "PNG")
                return Webcam.SAVED

            return Webcam.TOO_DARK

        logging.debug(self.file_isdiff(last_filename))

        if not self.file_isdiff(last_filename):
            logging.warning("Same as last image")
            return Webcam.SAME

        if self.image_average() >= avg:
            logging.info("Saving:\t\t\t%s", filename)
            self.image.save(filename, "PNG")
            return Webcam.SAVED

        return Webcam.TOO_DARK

    def grab_image(self, url):
        """
        Download an image from an URL.

        :param url: URL of the image
        """
        if url is None:
            logging.error("Error: No webcam URL")
            return

        response = requests.get(url)
        self.image = Image.open(BytesIO(response.content))

    def file_isdiff(self, filename):
        """
        Compare this image to a file.

        :param filename: File name of the image.
        :return: True if different.
        """
        diff = 0
        if self.image is None:
            logging.error("Error: No image data")
            return True

        fimage = Image.open(filename)

        spixels = list(self.image.getdata())
        fpixels = list(fimage.getdata())

        for pixel in range(0, len(spixels)):
            if spixels[pixel] != fpixels[pixel]:
                diff += 1

        logging.debug("Number of different pixels %d", diff)

        if diff < 10:
            return False

        return True

    def image_average(self):
        """
        Calculate the avrage B/W light level.

        :return: the avarage B/W level of the picture in percent
        """
        if self.image is None:
            logging.error("Error: No image data")
            return 100
        pixels = list(self.image.getdata())

        avg = 0
        npixels = 0

        for pixel in pixels:
            avg += (pixel[0] + pixel[1] + pixel[2]) / 3
            npixels += 1

        avg /= npixels
        percent = avg / 256 * 100
        logging.info("Light level:\t\t{:3.2f}%".format(percent))
        return percent


class Daytime(object):
    """
    Class that handles daytime information.

    Uses https://sunrise-sunset.org/ to get the daytime data.
    """

    def __init__(self, lat, lon):
        """
        Constructor.

        :param lat: Latitude of the camera location
        :param lon: Longetiude of the camera location
        """
        self.lat = lat
        self.long = lon
        self.up_time = None
        self.down_time = None

    def update(self):
        """
        Update daylight times from the remote API.
        """
        response = requests.get('https://api.sunrise-sunset.org/json?' +
                                'lat={}&lng={}&date=today'.format(self.lat,
                                                                  self.long))
        if response.ok:
            json_resp = response.text
            daytime = json.loads(json_resp)

            def get_utc(utc):
                """
                Add current date to 12 hour UTC time.

                :param utc: 12 hour UTC time
                :return: datetime.datetime object with UTC time + current date.
                """
                if utc[0] != '0' and utc[1] == ':':
                    utc = "0{}".format(utc)
                date = datetime.datetime.now().strftime("%Y-%m-%d ")
                utc_time = datetime.datetime.strptime(
                    date + utc, '%Y-%m-%d %I:%M:%S %p')
                return utc_time

            self.up_time = get_utc(
                daytime['results']['civil_twilight_begin'])
            self.down_time = get_utc(
                daytime['results']['civil_twilight_end'])
            logging.info("Daylight begins:\t\t%s",
                         self.up_time.strftime('%Y-%m-%d %H:%M:%S UTC'))
            logging.info("Daylight ends:\t\t%s",
                         self.down_time.strftime('%Y-%m-%d %H:%M:%S UTC'))

    def check_daylight(self):
        """
        Check if there is daylight.

        :return: True if in dayligth period, False otherwise
        """
        if self.up_time is None or self.down_time is None:
            logging.error("Error: No daytime information")
            return False

        current_time = datetime.datetime.utcnow()
        if current_time > self.up_time and current_time < self.down_time:
            return True

        return False

    def get(self):
        """
        Get daylight times.

        :return: Tuple of up time and down time
        """
        return (self.up_time, self.down_time)


TIMERS = {}


def named_timer(name, interval, function, *args, **kwargs):
    """Factory function to create named Timer objects.

      Timers call a function after a specified number of seconds:

          t = Timer('Name', 30.0, function)
          t.start()
          t.cancel()  # stop the timer's action if it's still waiting
    """
    timer = threading.Timer(interval, function, *args, **kwargs)
    timer.name = name
    TIMERS[name] = {}
    TIMERS[name]['start'] = datetime.datetime.now()
    TIMERS[name]['interval'] = interval
    return timer


def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('interval', type=int,
                        help='Interval betewwn grabs, in secends', default=60)
    parser.add_argument('url', type=str, help='URL of the image')
    parser.add_argument('target_dir', type=str, help='Target directory')
    parser.add_argument('-l, --light', type=int, dest='light_percent',
                        help="Image are discarded below this B/W light level " +
                        "in percent", default=0)
    parser.add_argument('-d, --daylight', nargs=2, default=[], dest='daylight',
                        help='Longetude and latitude to only grab during ' +
                        'astronomical daylight hours')
    args = parser.parse_args()

    logging.info("Interval:\t\t\t%d", args.interval)
    logging.info("URL:\t\t\t%s", args.url)
    logging.info("Directory:\t\t\t%s", args.target_dir)
    logging.info("Light level threshold:\t%d%%", args.light_percent)

    if len(args.daylight) == 2:
        daytime = Daytime(args.daylight[0], args.daylight[1])

        def daytime_worker():
            """
            Worker to update daytime and restart the thread waiting
            """
            logging.debug("Starting new daytime worker")
            daytime.update()
            daytime_thread = named_timer("DaytimeThread",
                                         21600,
                                         daytime_worker)
            daytime_thread.start()

        daytime_worker()
    else:
        daytime = None

    webcam = Webcam()

    def webcam_worker(last_filename, skipped, interval):
        """
        Worker to grab an image and restat the thread waiting
        """
        start_time = timeit.default_timer()
        logging.debug("Starting new webcam worker")
        filename = "{}.png".format(
            datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S_UTC'))
        grabbed = -1
        if daytime is None:
            # If we do not care about daytime, just grab the image
            grabbed = webcam.grab(last_filename, filename,
                                  args.light_percent, args.url)
        else:
            if daytime.check_daylight():
                grabbed = webcam.grab(
                    last_filename, filename, args.light_percent, args.url)
            else:
                daylight = daytime.get()
                interval = (
                    daylight[0] - datetime.datetime.utcnow()).total_seconds()
                if interval > 3600 or interval < 0:
                    interval = 3600
                logging.info("Waiting for day light")

        if grabbed == Webcam.SAVED:
            last_filename = filename
            skipped = 0
            interval = args.interval
        elif grabbed == Webcam.TOO_DARK:
            skipped += 1
            logging.info("Skipped...%d", skipped)
            if skipped >= 5:
                if skipped == 5:
                    logging.info("5 images skipped, increasing interval")
                interval *= 2
                if interval > 1500:
                    logging.info("Resetting interval")
                    interval = args.interval
        elif grabbed == Webcam.SAME:
            skipped += 1
            logging.info("Skipped...%d", skipped)

            if skipped >= 5:
                if skipped == 5:
                    logging.info("5 images skipped, increasing interval")
                interval *= 2
                if interval > 1500:
                    logging.info("Resetting interval")
                    interval = args.interval
            else:
                interval = 5

        interval -= timeit.default_timer() - start_time

        logging.info("Waiting {:.0f} seconds".format(interval))
        webcam_thread = named_timer("WebcamThread",
                                    interval,
                                    webcam_worker,
                                    args=(last_filename, skipped, interval))
        webcam_thread.start()

    webcam_worker(None, 0, args.interval)

    logging.info("All threads runnig, press CTRL-C to quit")
    seconds = 0
    main_thread = threading.currentThread()
    try:
        while True:
            time.sleep(1)
            seconds += 1
            if seconds > 900:
                seconds = 0
                for thread in threading.enumerate():
                    if thread is not main_thread:
                        elapsed = (datetime.datetime.now() -
                                   TIMERS[thread.name]['start']).total_seconds()
                        logging.info("Thread: %s", thread.name)
                        logging.info("\tWaited:\t\t%d seconds", elapsed)
                        logging.info("\tWaiting:\t%d seconds",
                                     TIMERS[thread.name]['interval'] - elapsed)
    except KeyboardInterrupt:
        logging.info("Stopping...")

    for thread in threading.enumerate():
        if thread is not main_thread:
            logging.debug('Stopping %s', thread.getName())
            thread.cancel()


if __name__ == "__main__":
    main()
