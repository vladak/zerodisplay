"""
command line parsing
"""

import argparse
import logging

from logutil import LogLevelAction


class TimeoutAction(argparse.Action):
    """
    handle the timeout argument, enforcing minimum value.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """
        initialize. do not allow nargs.
        """
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """
        set value. enforce minimum timeout.
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"{namespace}, {values}, {option_string}")
        if values < 180:
            raise ValueError("timeout must be bigger than 180")
        setattr(namespace, self.dest, values)


def parse_args(args=None):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(
        description="Update eInk paper display with weather metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--hostname",
        help="MQTT broker hostname",
        required=True,
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
        default=900,
        type=int,
        action=TimeoutAction,
    )
    parser.add_argument(
        "--metric_timeout",
        help="Timeout in seconds to consider metrics stale",
        default=1800,
        type=int,
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
        "-p",
        "--port",
        help="MQTT broker port",
        default=1883,
    )
    parser.add_argument(
        "-L",
        "--large_font",
        help="Large font path",
        default="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    )
    parser.add_argument(
        "--temp_sensor_topic",
        help="Temperature sensor MQTT topic",
        required=True,
    )
    parser.add_argument(
        "--temp_sensor_name",
        help="Temperature sensor MQTT name",
        required=True,
    )
    parser.add_argument(
        "--co2_sensor_topic",
        help="CO2 sensor MQTT topic",
        required=True,
    )
    parser.add_argument(
        "--co2_sensor_name",
        help="CO2 sensor MQTT name",
        required=True,
    )
    parser.add_argument(
        "--pressure_sensor_topic",
        help="Barometric pressure sensor MQTT topic",
        required=True,
    )
    parser.add_argument(
        "--pressure_sensor_name",
        help="Barometric pressure sensor MQTT name",
        required=True,
    )

    return parser.parse_args(args)
