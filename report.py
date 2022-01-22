#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import time
import requests

from datetime import datetime

import digitalio
import busio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.ssd1680 import Adafruit_SSD1680  # pylint: disable=unused-import

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
srcs = None
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

display = Adafruit_SSD1680(122, 250,  # 2.13" HD Tri-color or mono display
                           spi,
                           cs_pin=ecs,
                           dc_pin=dc,
                           sramcs_pin=srcs,
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

    r = requests.get(url)
    if r.status_code != 200:
        print(f"cannot retrieve metrics from {url}: {r.status_code}")
    else:
        lines = r.text.split("\n")
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


def update_display():
    temp, co2, pressure = get_metrics("http://weather:8111")

    image = Image.new("RGB", (display.width, display.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a filled box as the background
    draw.rectangle((0, 0, display.width - 1, display.height - 1), fill=BACKGROUND_COLOR)

    # Display time
    now = datetime.now()
    text = now.strftime("%H:%M").lstrip("0").replace(" 0", " ")
    print(text)
    (text_width, text_height) = medium_font.getsize(text)
    coords = (display.width - text_width - 10, 0)
    print(f"coordinates = {coords}")
    draw.text(
        coords,
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
    print(text)
    (text_width, text_height) = large_font.getsize(text)
    print(f"text width={text_width}, height={text_height}")
    print(f"display width={display.width}, height={display.height}")
    # coords = (display.width // 2 - text_width // 2, display.height // 2 - text_height // 2)
    coords = (0, 0)
    print(f"coordinates = {coords}")
    draw.text(
        coords,
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
    print(text)
    coords = (0, text_height + 10)  # use previous text height
    y = text_height + 10
    (text_width, text_height) = font.getsize(text)
    y = y + text_height
    print(f"coordinates = {coords}")
    draw.text(
        coords,
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
    print(text)
    coords = (0, y)  # use previous text height
    print(f"coordinates = {coords}")
    draw.text(
        coords,
        text,
        font=medium_font,
        fill=TEXT_COLOR,
    )

    # Display image.
    print("display in progress")
    display.image(image)
    display.display()
    print("display done")


if __name__ == "__main__":
    # TODO: argparse
    while True:
        update_display()
        time.sleep(120)
