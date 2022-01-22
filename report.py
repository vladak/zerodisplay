#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import time
import requests
import sys

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
FONTSIZE = 24
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

# Load a TTF Font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

# TODO: display current time

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64
)


def update_display():
    r = requests.get("http://weather:8111")
    if r.status_code != 200:
        # TODO: Draw the error on screen
        print("error")
        sys.exit(1)

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
    outside_temp = int(float(temp))
    text = f"{outside_temp}°C"
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
    # TODO: diplay warning sign if above threshold
    co2 = int(float(co2))
    text = f"CO2: {co2} ppm"
    print(text)
    # TODO: the +5 should be proportional to the previous text height
    coords = (0, text_height + 10)  # use previous text height
    y = text_height + 10
    (text_width, text_height) = font.getsize(text)
    y = y + text_height
    print(f"coordinates = {coords}")
    draw.text(
        coords,
        text,
        font=font,
        fill=TEXT_COLOR,
    )

    # Display atmospheric pressure level.
    pressure = int(float(pressure))
    text = f"Pressure: {pressure} hPa"
    print(text)
    coords = (0, y)  # use previous text height
    print(f"coordinates = {coords}")
    draw.text(
        coords,
        text,
        font=font,
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
