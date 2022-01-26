#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import argparse
import logging
import time
import sys
from datetime import datetime

try:
    import board
    import busio
    import digitalio
except NotImplementedError as exc:
    print(f"Will only support running with -o: {exc}")
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

    try:
        response = requests.get(url)
    except requests.ConnectionError as req_exc:
        logger.error(f"cannot get data from {url}: {req_exc}")
        return temp, co2, pressure

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


def get_e_ink_display(height, width):
    """
    :return: eInk display instance
    """
    # Create the SPI device and pins we will need.
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    ecs = digitalio.DigitalInOut(board.CE0)
    # pylint: disable=invalid-name
    dc = digitalio.DigitalInOut(board.D22)
    rst = digitalio.DigitalInOut(board.D27)
    busy = digitalio.DigitalInOut(board.D17)

    display = Adafruit_SSD1680(
        height,
        width,
        spi,
        cs_pin=ecs,
        dc_pin=dc,
        sramcs_pin=None,
        rst_pin=rst,
        busy_pin=busy,
    )

    display.rotation = 1

    return display


def draw_image(url, display_width, display_height, medium_font_path, large_font_path):
    """
    Refresh the display with weather metrics retrieved from the URL
    :param large_font_path: path to font used for large letters
    :param medium_font_path: path to font used for medium letters
    :param display_height: display width in pixels
    :param display_width: display height in pixels
    :param url: URL to retrieve the metrics from
    :return PIL image instance
    """

    medium_font = ImageFont.truetype(medium_font_path, 24)
    large_font = ImageFont.truetype(large_font_path, 64)

    temp, co2, pressure = get_metrics(url)

    image = Image.new("RGB", (display_width, display_height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a filled box as the background
    draw.rectangle((0, 0, display_width - 1, display_height - 1), fill=BACKGROUND_COLOR)

    draw_date_time(display_width, draw, medium_font)

    text_height = draw_outside_temperature(draw, temp, display_height, display_width, large_font)
    current_height = draw_co2(draw, co2, text_height, medium_font)
    draw_pressure(current_height, draw, medium_font, pressure)

    return image


def draw_pressure(current_height, draw, medium_font, pressure):
    """
    :param current_height:
    :param draw:
    :param medium_font:
    :param pressure:
    :return:
    """
    logger = logging.getLogger(__name__)

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


def draw_co2(draw, co2, text_height, medium_font):
    """
    :param draw:
    :param co2:
    :param text_height:
    :param medium_font:
    :return: current text height
    """
    logger = logging.getLogger(__name__)

    # Display CO2 level.
    if co2:
        co2 = int(float(co2))
        text = f"CO2: {co2} ppm"
    else:
        text = "CO2: N/A"
    logger.debug(text)
    coordinates = (0, text_height + 10)  # use previous text height
    current_height = text_height + 10
    (_, text_height) = medium_font.getsize(text)
    current_height = current_height + text_height
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )
    return current_height


def draw_outside_temperature(draw, temp, display_height, display_width, large_font):
    """
    :param draw:
    :param temp:
    :param display_height:
    :param display_width:
    :param large_font:
    :return: current text height
    """
    logger = logging.getLogger(__name__)

    # Display outside temperature.
    if temp:
        outside_temp = int(float(temp))
        text = f"{outside_temp}°C"
    else:
        text = "N/A"
    logger.debug(text)
    (text_width, text_height) = large_font.getsize(text)
    logger.debug(f"text width={text_width}, height={text_height}")
    logger.debug(f"display width={display_width}, height={display_height}")
    coordinates = (0, 0)
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=large_font,
        fill=TEXT_COLOR,
    )
    return text_height


def draw_date_time(display_width, draw, medium_font):
    """
    Draw date and time in the right top corner.
    :param display_width:
    :param draw:
    :param medium_font:
    :return:
    """
    logger = logging.getLogger(__name__)

    # Display time.
    now = datetime.now()
    text = now.strftime(f"{now.hour}:%M")
    logger.debug(text)
    (text_width, text_height) = medium_font.getsize(text)
    coordinates = (display_width - text_width - 10, 0)
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )
    # Display date underneath the time.
    text = now.strftime(f"{now.day}.{now.month}.")
    logger.debug(text)
    coordinates = (display_width - text_width - 10, text_height + 5)
    logger.debug(f"coordinates = {coordinates}")
    draw.text(
        coordinates,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )


def update_e_ink_display(display, image):
    """
    Display image.
    :param display:
    :param image:
    :return:
    """
    logger = logging.getLogger(__name__)

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
    parser.add_argument(
        "-o",
        "--output",
        help="Instead of updating the display, print the image to a JPG file",
    )
    parser.add_argument(
        "-m",
        "--medium_font",
        help="Medium font path",
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    parser.add_argument(
        "-L",
        "--large_font",
        help="Large font path",
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )

    return parser.parse_args()


def main():
    """
    The main function. Parses args and runs infinite loop to update the display.
    """
    args = parse_args()

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)

    # 2.13" HD Tri-color or mono display
    display_height = 122
    display_width = 250

    if args.output:
        image = draw_image(args.url, display_width, display_height,
                           args.medium_font, args.large_font)
        image.save(args.output)
        return

    display = get_e_ink_display(display_height, display_width)
    while True:
        image = draw_image(args.url, display.width, display.height,
                           args.medium_font, args.large_font)
        update_e_ink_display(display, image)
        time.sleep(args.timeout)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
