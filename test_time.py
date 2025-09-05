"""
Test how the main loop behaves in time.
"""

import time
import unittest.mock

import pytest

from display import Display
from loop_cond import CondLimit
from metrics import Metrics
from metrics_drawer import MetricsDrawer
from report import loop


def mock_image_update(image):
    """
    The purpose of this function is to record the times of the calls
    to the update() function of the Display object.
    :param image: Image object (mock)
    """
    image.call_times.append(time.monotonic())


@pytest.mark.parametrize("timeout", [1, 3])
def test_loop(timeout):
    """
    Ensure that the display is not updated more often than the specified timeout
    in the main loop.
    """
    metrics_attrs = {"get_metrics.return_value": (1, 2, 3)}
    metrics_mock = unittest.mock.Mock(spec=Metrics, **metrics_attrs)
    display_attrs = {"update.side_effect": mock_image_update}
    display_mock = unittest.mock.Mock(spec=Display, **display_attrs)
    mock_image = unittest.mock.Mock()
    mock_image.call_times = []
    drawer_attrs = {"draw_image.return_value": mock_image}
    drawer_mock = unittest.mock.Mock(spec=MetricsDrawer, **drawer_attrs)
    iter_count = 3

    # Run the loop for specified number of iterations.
    before = time.monotonic()
    loop(CondLimit(iter_count), timeout, drawer_mock, display_mock, metrics_mock)
    after = time.monotonic()

    # Total elapsed time needs to match the timeout and number of iterations.
    assert after - before > timeout * iter_count

    # The calls to display.update() should match the number of iterations and be spaced apart.
    display_mock.update.assert_has_calls(
        [unittest.mock.call(mock_image) for _ in range(iter_count)]
    )
    int_list = mock_image.call_times
    for diff in [
        int_list[i] - int_list[i - 1] for i in range(len(int_list) - 1, 0, -1)
    ]:
        assert diff > timeout
