"""
set of classes to implement condition checking.
Useful for testing.
"""

import abc


class FormalCondInterface(metaclass=abc.ABCMeta):
    """
    to make classes implement the cond() function.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "cond") and callable(subclass.cond) or NotImplemented

    @abc.abstractmethod
    def cond(self):
        """Load in the data set"""
        raise NotImplementedError


# pylint: disable=too-few-public-methods
class CondLimit(FormalCondInterface):
    """
    condition with limit
    """

    def __init__(self, limit):
        """
        :param limit: number of times the cond() function should return True
        """
        if limit < 0:
            raise ValueError("limit must be positive")

        self.limit = limit
        self.counter = 0

    def cond(self):
        """
        :return: whether to continue
        """
        self.counter += 1
        if self.counter > self.limit:
            return False

        return True


# pylint: disable=too-few-public-methods
class CondInfinite(FormalCondInterface):
    """
    condition without limit
    """

    def __init__(self):
        """no-op"""

    def cond(self):
        """
        :return: True
        """
        return True
