"""
display classes
"""

import logging

try:
    import board
    import busio
    import digitalio
except NotImplementedError as exc:
    print(f"Will only support running with -o: {exc}")

from adafruit_epd.ssd1680 import Adafruit_SSD1680
from inky.auto import auto


# pylint: disable=too-few-public-methods
class Display:
    """
    class to wrap the eInk display
    """

    def __init__(self, display, width, height):
        """
        initialize
        """
        self.display = display
        self.width = width
        self.height = height

    def update(self, image):
        """
        Display image.
        :param display: Display object
        :param image:
        :return:
        """


# pylint: disable=too-few-public-methods
class AdafruitDisplay(Display):
    """
    class to wrap the Adafruit eInk display
    """

    def update(self, image):
        """
        Display image.
        :param image: image to display
        :return:
        """
        logger = logging.getLogger(__name__)

        logger.debug("display in progress")
        self.display.image(image)
        self.display.display()
        logger.debug("display done")


# pylint: disable=too-few-public-methods
class InkyDisplay(Display):
    """
    class to wrap the Pimoroni pHAT eInk display
    """

    def update(self, image):
        """
        Display image.
        :param image: image to display
        :return:
        """
        logger = logging.getLogger(__name__)

        logger.debug("display in progress")
        self.display.set_image(image)
        self.display.show()
        logger.debug("display done")


def get_e_ink_display():
    """
    :return: Display instance
    """
    logger = logging.getLogger(__name__)

    try:
        # Create the SPI device and pins we will need.
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        ecs = digitalio.DigitalInOut(board.CE0)
        # pylint: disable=invalid-name
        dc = digitalio.DigitalInOut(board.D22)
        rst = digitalio.DigitalInOut(board.D27)
        busy = digitalio.DigitalInOut(board.D17)

        # 2.13" HD Tri-color or mono display
        display_height = 122
        display_width = 250

        display = Adafruit_SSD1680(
            display_height,
            display_width,
            spi,
            cs_pin=ecs,
            dc_pin=dc,
            sramcs_pin=None,
            rst_pin=rst,
            busy_pin=busy,
        )

        display.rotation = 1
        logger.info("Detected Adafruit SSD1680 display")
        return AdafruitDisplay(display, display_width, display_height)
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    # Fall back to Pimoroni pHAT.
    try:
        display = auto()
        logger.info("Detected Pimoroni pHAT")
        return InkyDisplay(display, display.resolution[0], display.resolution[1])
    except RuntimeError as e:
        logger.error("cannot initialize inky pHAT: {e}")
        return None
