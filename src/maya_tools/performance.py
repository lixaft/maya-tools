"""Provide utilities to measure performance."""
from __future__ import division

import contextlib
import cProfile
import logging
import pstats
import time
from typing import Generator

from maya import cmds

__all__ = ["fps", "profile", "timing"]

LOG = logging.getLogger(__name__)


def fps(loop=5, mode="parallel", gpu=True, cache=False, renderer="vp2"):
    # pylint: disable=unused-argument
    """Measure the fps of the current scene.

    It take the active range of the scene, play it view time and show the
    result in the stdout.

    The values for the evulation mode parameter are (the case does not matter):

    Arguments:
        loop (int): The number of times the test should be run.
        mode (str): The evaluation mode to use.
        gpu (bool): Turn on/off the gpu override.
        cache (bool): Turn on/off the cached playback.
        renderer (str): The viewport that will be used to run the test.
    """
    panel = cmds.getPanel(withFocus=True)

    # Set the playback speed to free
    playback_spped = cmds.playbackOptions(query=True, playbackSpeed=True)
    cmds.playbackOptions(edit=True, playbackSpeed=0)

    # Set the viewport renderer
    current_renderer = cmds.modelEditor(panel, query=True, rendererName=True)
    args = {"vp1": "base_OpenGL_Renderer", "vp2": "vp2Renderer"}
    arg = args.get(renderer.lower(), renderer)
    cmds.modelEditor(panel, edit=True, rendererName=arg)

    # Set the evaluation mode
    current_mode = cmds.evaluationManager(query=True, mode=True)[0]
    args = {
        "emp": "parallel",
        "ems": "serial",
        "dg": "off",
        "//": "parallel",
        "->": "off",
    }
    cmds.evaluationManager(mode=args.get(mode.lower(), mode.lower()))

    # Disable cycle check
    cycle_check = cmds.cycleCheck(query=True, evaluation=True)
    cmds.cycleCheck(evaluation=False)

    # Run performance test
    results = []
    current_frame = cmds.currentTime(query=True)
    start_frame = cmds.playbackOptions(query=True, minTime=True)
    end_frame = cmds.playbackOptions(query=True, maxTime=True)
    frame_range = end_frame - start_frame
    for _ in range(loop):
        cmds.currentTime(start_frame)
        start_time = time.time()
        cmds.play(wait=True)
        end_time = time.time()
        result = end_time - start_time
        results.append(round(frame_range / result))
    cmds.currentTime(current_frame)

    # Restore the configuration
    cmds.playbackOptions(edit=True, playbackSpeed=playback_spped)
    cmds.modelEditor(panel, edit=True, rendererName=current_renderer)
    cmds.evaluationManager(mode=current_mode)
    cmds.cycleCheck(evaluation=cycle_check)

    # Display the result
    msg = "PERFORMANCE TEST\n"
    msg += "=" * (len(msg) - 1) + "\n\n"
    for result in results:
        msg += "\t- {} FPS\n".format(result)

    msg += "\n\tMIN: {} FPS".format(min(results))
    msg += "\n\tMAX: {} FPS".format(max(results))
    msg += "\n\n\tAVERAGE: {} FPS".format(round((sum(results) / len(results))))

    LOG.info("\n\n\n%s\n\n\n", msg)


@contextlib.contextmanager
def profile(sort="time", lines=None, strip=False):
    """Detail the execution of all statements in the block.

    The following are the values accepted by the ``sort`` parameter:

    Arguments:
        sort (str): Sorts the output according to the specified mode.
        lines (int): Limits the output to a specified number of lines.
        strip (bool): Removes all leading path information from file name.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    yield
    profiler.disable()

    stats = pstats.Stats(profiler)
    if strip:
        stats.strip_dirs()
    stats.sort_stats(sort)
    stats.print_stats(lines)


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
