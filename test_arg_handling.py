"""
Test argument handling.
"""

import pytest

from cli import parse_args


@pytest.mark.parametrize("timeout", [0, -1, 1, 179])
def test_invalid_timeout(timeout):
    """
    invalid timeout values should raise ValueError
    :param timeout: timeout in seconds
    """
    with pytest.raises(ValueError):
        parse_args(["--timeout", str(timeout)])


required_options = [
    "--hostname",
    "example.com",
    "--temp_sensor_topic",
    "foo",
    "--temp_sensor_name",
    "foo",
    "--co2_sensor_topic",
    "foo",
    "--co2_sensor_name",
    "foo",
    "--pressure_sensor_topic",
    "foo",
    "--pressure_sensor_name",
    "foo",
]


@pytest.mark.parametrize("timeout", [180, 300, 600, 900])
def test_valid_timeout(timeout):
    """
    valid timeout values should result in the appropriate member to be set.
    :param timeout: timeout in seconds
    """
    args = parse_args(["--timeout", str(timeout)] + required_options)
    assert args.timeout == timeout
