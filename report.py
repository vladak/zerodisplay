#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import argparse
import logging
import sys
import time

try:
    import board
    import busio
    import digitalio
except NotImplementedError as exc:
    print(f"Will only support running with -o: {exc}")
from adafruit_epd.ssd1680 import Adafruit_SSD1680

from display import Display
from logutil import LogLevelAction


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
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    parser.add_argument(
        "-L",
        "--large_font",
        help="Large font path",
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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

    display = Display(
        args.url, display_width, display_height, args.medium_font, args.large_font
    )
    if args.output:
        image = display.draw_image()
        image.save(args.output)
        return

    e_display = get_e_ink_display(display_height, display_width)
    display = Display(
        args.url, e_display.width, e_display.height, args.medium_font, args.large_font
    )
    while True:
        image = display.draw_image()
        update_e_ink_display(e_display, image)
        time.sleep(args.timeout)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
