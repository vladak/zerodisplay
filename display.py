"""
display class

Not dependent on the output type.
"""

import logging
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont


class Display:
    """
    Class to wrap fetching and drawing of the metrics.
    """

    # First define some color constants
    WHITE = (0xFF, 0xFF, 0xFF)
    BLACK = (0x00, 0x00, 0x00)

    # Next define some constants to allow easy resizing of shapes and colors
    BACKGROUND_COLOR = WHITE
    FOREGROUND_COLOR = WHITE
    TEXT_COLOR = BLACK

    def __init__(self, url, display_width, display_height, medium_font_path, large_font_path):
        """
        :param url: URL to retrieve the metrics from
        :param display_height: display width in pixels
        :param display_width: display height in pixels
        :param large_font_path: path to font used for large letters
        :param medium_font_path: path to font used for medium letters
        """
        self.url = url
        self.display_width = display_width
        self.display_height = display_height

        self.small_font = ImageFont.truetype(large_font_path, 12)
        self.medium_font = ImageFont.truetype(medium_font_path, 24)
        self.large_font = ImageFont.truetype(large_font_path, 64)

        self.image = Image.new("RGB", (self.display_width, self.display_height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

    def get_metrics(self):
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
            response = requests.get(self.url)
        except requests.ConnectionError as req_exc:
            logger.error(f"cannot get data from {self.url}: {req_exc}")
            return temp, co2, pressure

        if response.status_code != 200:
            logger.error(
                f"cannot retrieve metrics from {self.url}: {response.status_code}"
            )
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

    def draw_image(self):
        """
        Refresh the display with weather metrics retrieved from the URL
        :return PIL image instance
        """

        temp, co2, pressure = self.get_metrics()

        # Draw a filled box as the background
        self.draw.rectangle(
            (0, 0, self.display_width - 1, self.display_height - 1),
            fill=Display.BACKGROUND_COLOR,
        )

        self.draw_date_time()

        text_height = self.draw_outside_temperature(temp)
        current_height = self.draw_co2(co2, text_height)
        self.draw_pressure(current_height, pressure)

        return self.image

    def draw_pressure(self, current_height, pressure):
        """
        :param current_height:
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
        self.draw.text(
            coordinates,
            text,
            font=self.medium_font,
            fill=Display.TEXT_COLOR,
        )

    def draw_co2(self, co2, text_height):
        """
        :param co2:
        :param text_height:
        :return: current text height
        """
        logger = logging.getLogger(__name__)

        # Display CO2 level.
        co_text = "CO"
        if co2:
            co2 = int(float(co2))
            text = f"{co_text} : {co2} ppm"
        else:
            text = f"{co_text} : N/A"
        coordinates = (0, text_height + 10)  # use previous text height
        current_height = text_height + 10
        (_, text_height) = self.medium_font.getsize(text)
        current_height = current_height + text_height
        logger.debug(f"'{text}' coordinates = {coordinates}")
        self.draw.text(
            coordinates,
            text,
            font=self.medium_font,
            fill=Display.TEXT_COLOR,
        )

        (co_width, _) = self.medium_font.getsize(co_text)
        coordinates = (co_width, current_height - 10)
        logger.debug(f"'2' coordinates = {coordinates}")
        self.draw.text(
            coordinates,
            "2",
            font=self.small_font,
            fill=Display.TEXT_COLOR,
        )

        return current_height

    def draw_outside_temperature(self, temp):
        """
        :param temp: temperature value
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
        (text_width, text_height) = self.large_font.getsize(text)
        logger.debug(f"text width={text_width}, height={text_height}")
        logger.debug(
            f"display width={self.display_width}, height={self.display_height}"
        )
        coordinates = (0, 0)
        logger.debug(f"coordinates = {coordinates}")
        self.draw.text(
            coordinates,
            text,
            font=self.large_font,
            fill=Display.TEXT_COLOR,
        )
        return text_height

    def draw_date_time(self):
        """
        Draw date and time in the top right corner.
        """
        logger = logging.getLogger(__name__)

        # Display time.
        now = datetime.now()
        text = now.strftime(f"{now.hour}:%M")
        logger.debug(text)
        (text_width, text_height) = self.medium_font.getsize(text)
        coordinates = (self.display_width - text_width - 10, 0)
        logger.debug(f"coordinates = {coordinates}")
        self.draw.text(
            coordinates,
            text,
            font=self.medium_font,
            fill=Display.TEXT_COLOR,
        )
        # Display date underneath the time.
        text = now.strftime(f"{now.day}.{now.month}.")
        logger.debug(text)
        coordinates = (self.display_width - text_width - 10, text_height + 5)
        logger.debug(f"coordinates = {coordinates}")
        self.draw.text(
            coordinates,
            text,
            font=self.medium_font,
            fill=Display.TEXT_COLOR,
        )
