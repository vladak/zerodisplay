#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import argparse
import logging
import time
from datetime import datetime

import board
import busio
import digitalio
import requests
from adafruit_epd.ssd1680 import Adafruit_SSD1680
from PIL import Image, ImageDraw, ImageFont

from logutil import LogLevelAction

# First define some color constants
WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x00, 0x00, 0x00)

# Next define some constants to allow easy resizing of shapes and colors
BACKGROUND_COLOR = WHITE
FOREGROUND_COLOR = WHITE
TEXT_COLOR = BLACK

# create the spi device and pins we will need
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

display = Adafruit_SSD1680(
    122,
    250,  # 2.13" HD Tri-color or mono display
    spi,
    cs_pin=ecs,
    dc_pin=dc,
    sramcs_pin=None,
    rst_pin=rst,
    busy_pin=busy,
)

display.rotation = 1

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64
)


def get_metrics(url):
    """
    Retrieve metrics from given URL and return them. If a metric cannot be retrieved,
    None is used instead.
    :return: tuple of temperature, CO2, atmospheric pressure
    """
    temp = None
    co2 = None
    pressure = None

    logger = logging.getLogger(__name__)

    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"cannot retrieve metrics from {url}: {response.status_code}")
    else:
        lines = response.text.split("\n")
        for line in lines:
            if line.startswith("weather_temp_terasa"):
                _, temp = line.split()
                continue

            if line.startswith("co2_ppm"):
                _, co2 = line.split()
                continue

            if line.startswith("pressure_sea_level_hpa"):
                _, pressure = line.split()
                continue

    return temp, co2, pressure


def update_display(url):
    """
    Refresh the display with weather metrics retrieved from the URL
    :param url: URL to retrieve the metrics from
    """
    logger = logging.getLogger(__name__)

    temp, co2, pressure = get_metrics(url)

    image = Image.new("RGB", (display.width, display.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a filled box as the background
    draw.rectangle((0, 0, display.width - 1, display.height - 1), fill=BACKGROUND_COLOR)

    # Display time
    now = datetime.now()
    text = now.strftime("%H:%M").lstrip("0").replace(" 0", " ")
    logger.debug(text)
    (text_width, text_height) = medium_font.getsize(text)
    coordinates = (display.width - text_width - 10, 0)
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )

    # Display outside temperature.
    if temp:
        outside_temp = int(float(temp))
        text = f"{outside_temp}°C"
    else:
        text = "N/A"
    logger.debug(text)
    (text_width, text_height) = large_font.getsize(text)
    logger.debug(f"text width={text_width}, height={text_height}")
    logger.debug(f"display width={display.width}, height={display.height}")
    coordinates = (0, 0)
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=large_font,
        fill=TEXT_COLOR,
    )

    # Display CO2 level.
    if co2:
        co2 = int(float(co2))
        text = f"CO2: {co2} ppm"
    else:
        text = "CO2: N/A"
    logger.debug(text)
    coordinates = (0, text_height + 10)  # use previous text height
    current_height = text_height + 10
    (text_width, text_height) = medium_font.getsize(text)
    current_height = current_height + text_height
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )

    # Display atmospheric pressure level.
    if pressure:
        pressure = int(float(pressure))
        text = f"Pressure: {pressure} hPa"
    else:
        text = "Pressure: N/A"
    logger.debug(text)
    coordinates = (0, current_height)  # use previous text height
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )

    # Display image.
    logger.debug("display in progress")
    display.image(image)
    display.display()
    logger.debug("display done")


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        description="Update eInk paper display with weather metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        action=LogLevelAction,
        help='Set log level (e.g. "ERROR")',
        default=logging.INFO,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="Timeout in seconds to sleep between updating the display",
        default=120,
    )
    parser.add_argument(
        "--url",
        help="URL to query for metrics in Prometheus format",
        default="http://weather:8111",
    )

    return parser.parse_args()


def main():
    """
    The main function. Parses args and runs infinite loop to update the display.
    :return:
    """
    args = parse_args()

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    while True:
        update_display(args.url)
        time.sleep(args.timeout)


if __name__ == "__main__":
    main()
