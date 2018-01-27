#!/bin/env python3
"""
Grab an image off the internet at regular intervals.
"""
import re
import requests
from bs4 import BeautifulSoup


def main():
    """
    Main entry point
    """
    response = requests.get('http://www.stvedas.co.uk/webcam.htm')
    if response.ok:
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        webcam_url = soup.find("iframe")['src']
        response = requests.get(webcam_url)
        if response.ok:
            html = response.text
            pattern = re.compile(r"\s*var\s*streamid\s*=\s*\'([a-zA-Z0-9]+)\'")
            print("http://s10.ipcamlive.com/streams/{}/snapshot.jpg".format(pattern.search(html).group(1)))


if __name__ == "__main__":
    main()
