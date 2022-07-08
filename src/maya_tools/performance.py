"""Provide utilities to measure performance."""
from __future__ import division

import contextlib
import cProfile
import logging
import pstats
import time
from typing import Generator, Union

__all__ = ["profile", "timing"]

LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def profile(restrictions=10, sort="time", strip=False):
    # type: (Union[int, float, str], str, bool) -> Generator[None, None, None]
    """Detail the execution of all statements in the block.

    The following are the values accepted by the ``sort`` parameter:

    Arguments:
        restrictions: Limit the list down to the significant entries.
        sort: Sorts the output according to the specified mode.
        strip: Removes all leading path information from file name.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    yield
    profiler.disable()

    stats = pstats.Stats(profiler)
    if strip:
        stats.strip_dirs()
    stats.sort_stats(sort)
    stats.print_stats(restrictions)


@contextlib.contextmanager
def timing(name, unit="millisecond", message="{name}: {time:.3f} {unit}"):
    # type: (str, str, str) -> Generator[None, None, None]
    """Measure the time required to execute a block.

    Its possible to specify a unit for the time value using the ``unit``
    parameter. The possible values are: ``minute``, ``second``,
    ``millisecond``, ``microsecond``, ``nanosecond``.

    The ``message`` parameter correspond to the text that will be displayed in
    int the stdout. The string will be formatted using the ``str.format()``
    method. Using this method, some keys are available inside the string:

    - ``name``: The name of the executed block.
    - ``unit``: The unit specified in parameter.
    - ``time``: The time that the function took to be completed.

    Arguments:
        name (str): The name of the block that will be used inside the
            ``message`` paremeter.
        unit (str):  The unit of time in which the execution time is displayed.
        message (str): The output message displayed after execution.
    """
    start = time.time()
    yield
    end = time.time()
    multiplier = {
        "minute": 1 / 60,
        "second": 1,
        "millisecond": 1e3,
        "microsecond": 1e6,
        "nanosecond": 1e9,
    }
    exec_time = (end - start) * multiplier[unit]
    LOG.info(message.format(name=name, time=exec_time, unit=unit))
