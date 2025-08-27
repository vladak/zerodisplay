"""
Metrics class abstracts acquiring metrics (to a degree)
"""

import json
import logging
import socket
import ssl
import time

import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException


def message_handler(client, topic, message):
    """
    process MQTT message and store the data in the Metrics object passed
    as a user data inside the MQTT client object.
    """
    metrics = client.user_data
    assert metrics

    logger = logging.getLogger(__name__)
    logger.debug(f"got {message} on {topic}")

    if topic not in [metrics.temp_topic, metrics.co2_topic, metrics.pressure_topic]:
        return

    payload_dict = json.loads(message)
    if topic == metrics.temp_topic:
        metrics.temp_value = payload_dict.get(metrics.temp_name)
        metrics.temp_ts = time.monotonic()
    if topic == metrics.co2_topic:
        metrics.co2_value = payload_dict.get(metrics.co2_name)
        metrics.co2_ts = time.monotonic()
    if topic == metrics.pressure_topic:
        metrics.pressure_value = payload_dict.get(metrics.pressure_name)
        metrics.pressure_ts = time.monotonic()


# pylint: disable=too-few-public-methods
class Metrics:
    """
    class to retrieve metrics
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-instance-attributes
    def __init__(
        self,
        hostname,
        port,
        metric_timeout,
        temp_topic,
        temp_name,
        co2_topic,
        co2_name,
        pressure_topic,
        pressure_name,
    ):
        """
        Connect to the MQTT broker and subcribe to the topics.
        """

        self.logger = logging.getLogger(__name__)

        self.mqtt = MQTT.MQTT(
            broker=hostname,
            port=port,
            socket_pool=socket,
            ssl_context=ssl.create_default_context(),
            user_data=self,
        )
        self.logger.info(f"Connecting to MQTT broker {hostname} on port {port}")
        self.mqtt.connect()

        self.metric_timeout = metric_timeout

        self.temp_topic = temp_topic
        self.temp_name = temp_name
        self.co2_topic = co2_topic
        self.co2_name = co2_name
        self.pressure_topic = pressure_topic
        self.pressure_name = pressure_name

        # The stored values and timestamps of their last update.
        self.temp_value = None
        self.temp_ts = None
        self.co2_value = None
        self.co2_ts = None
        self.pressure_value = None
        self.pressure_ts = None

        self.mqtt.on_message = message_handler
        topics = [(temp_topic, 0), (co2_topic, 0), (pressure_topic, 0)]
        self.logger.info(f"subscribing to {topics}")
        self.mqtt.subscribe(topics)

    def get_metrics(self):
        """
        Retrieve metrics from MQTT return them as a tuple.
        Should be called periodically w.r.t. MQTT timeout.
        If a metric cannot be retrieved, None is used instead.
        :return: tuple of temperature, CO2, atmospheric pressure
        """

        # Make sure to stay connected to the broker e.g. in case of keep alive.
        try:
            self.mqtt.loop(1)
        except MMQTTException as e:
            self.logger.warning(f"Got MQTT exception: {e}")
            self.mqtt.reconnect()

        #
        # If some of the metrics has not been updated for certain time,
        # consider it not available to avoid presenting stale values.
        #
        now = time.monotonic()
        if now > self.metric_timeout:
            time_threshold = now - self.metric_timeout
            if self.temp_ts is not None and self.temp_ts < time_threshold:
                self.logger.warning("temp updated before time threshold")
                self.temp_value = None
            if self.co2_ts is not None and self.co2_ts < time_threshold:
                self.logger.warning("co2 updated before time threshold")
                self.co2_value = None
            if self.pressure_ts is not None and self.pressure_ts < time_threshold:
                self.logger.warning("pressure updated before time threshold")
                self.pressure_value = None

        self.logger.debug(f"temp = {self.temp_value}")
        self.logger.debug(f"co2 = {self.co2_value}")
        self.logger.debug(f"pressure = {self.pressure_value}")

        return self.temp_value, self.co2_value, self.pressure_value
