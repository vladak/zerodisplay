#!/usr/bin/env python3

"""
Display weather metrics on ePaper.
"""

import logging
import sys
import time

from cli import parse_args
from display import get_e_ink_display
from loop_cond import CondInfinite, FormalCondInterface
from metrics import Metrics
from metrics_drawer import MetricsDrawer


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
    data = ()
    for _ in range(0, args.timeout):
        data = metrics.get_metrics()
        logger.debug(f"Metrics: {data}")
        if all(data):
            break
        time.sleep(1)
    logger.info("Done waiting for the metrics")
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

    loop(CondInfinite(), args.timeout, drawer, e_display, metrics)


def loop(cond, timeout, drawer, e_display, metrics):
    """
    infinite loop that retrieves the metrics and updates the display.
    :param cond: object implementing FormalCondInterface
    :param timeout: timeout in seconds
    :param drawer: MetricsDrawer object
    :param e_display: display object
    :param metrics: Metrics object
    """
    logger = logging.getLogger(__name__)

    assert isinstance(cond, FormalCondInterface)

    redraw_ts = 0
    while cond.cond():
        data = metrics.get_metrics()
        logger.debug(f"Metrics: {data}")
        now = time.monotonic()
        if redraw_ts == 0 or now - redraw_ts > timeout:
            logger.info("Drawing image")
            image = drawer.draw_image(*data)
            e_display.update(image)
            redraw_ts = now

        logger.debug(f"Sleeping for {timeout} seconds")
        time.sleep(timeout)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
