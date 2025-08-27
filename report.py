#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import argparse
import logging
import sys
import time

from display import get_e_ink_display
from logutil import LogLevelAction
from metrics import Metrics
from metrics_drawer import MetricsDrawer


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


def parse_args():
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

    metrics = Metrics(
        args.hostname,
        args.port,
        args.metric_timeout,
        args.temp_sensor_topic,
        args.temp_sensor_name,
        args.co2_sensor_topic,
        args.co2_sensor_name,
        args.pressure_sensor_topic,
        args.pressure_sensor_name,
    )

    drawer = MetricsDrawer(
        display_width,
        display_height,
        args.medium_font,
        args.large_font,
    )
    #
    # Wait for the metrics to become available.
    # Repurpose the refresh timeout for this.
    #
    logger.info("Waiting for the metrics")
    for _ in range(0, args.timeout):
        data = metrics.get_metrics()
        logger.debug(f"Metrics: {data}")
        if all(data):
            break
        time.sleep(1)
    if None in data:
        logger.warning(f"Some metrics are missing: {data}")

    if args.output:
        image = drawer.draw_image(*data)
        image.save(args.output)
        return

    logger.debug("Getting display")
    e_display = get_e_ink_display()
    if e_display is None:
        logger.error("No display detected")
        sys.exit(1)
    logger.debug(f"Got e-display: {e_display.display}")
    drawer = MetricsDrawer(
        e_display.width,
        e_display.height,
        args.medium_font,
        args.large_font,
    )
    redraw_ts = 0
    while True:
        data = metrics.get_metrics()
        logger.debug(f"Metrics: {data}")
        now = time.monotonic()
        if redraw_ts == 0 or now - redraw_ts > args.timeout:
            logger.info("Drawing image")
            image = drawer.draw_image(*data)
            e_display.update(image)
            redraw_ts = now

        logger.debug(f"Sleeping for {args.timeout} seconds")
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
