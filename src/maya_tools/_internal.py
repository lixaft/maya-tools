"""Internal utilities to manage the functions inside the package."""
import contextlib
import functools
import logging
import sys
from typing import Any, Callable, Optional

from maya import cmds

__all__ = ["with_maya"]

LOG = logging.getLogger(__name__)


def with_maya(minimum=None, maximum=None):
    # type: (Optional[int], Optional[int]) -> Callable[..., Any]
    """Ensure the version of maya before executing the function.

    Examples:
        >>> @with_maya(minimum=2030)
        ... def foo():
        ...     pass
        >>> foo()
        Traceback (most recent call last):
          ...
        RuntimeError

    Arguments:
        minimum(int): The minimum supported version of maya.
        maximum(int): The maximum supported version of maya.

    Returns:
        function: The decoratoed function.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            version = int(cmds.about(version=True))
            if minimum is not None and version < minimum:
                msg = "Invalid maya version. min={} max={} current={}"
                raise RuntimeError(msg.format(minimum, maximum, version))
            if maximum is not None and version > maximum:
                msg = "Invalid maya version. min={} max={} current={}"
                raise RuntimeError(msg.format(minimum, maximum, version))

            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextlib.contextmanager
def nested_managers(*managers):
    """Combine multiple context managers into a single nested context manager.

    This function has been deprecated in favour of the multiple manager form
    of the with statement.

    The one advantage of this function over the multiple manager form of the
    with statement is that argument unpacking allows it to be
    used with a variable number of context managers as follows:

       with nested(*managers):
           do_something()

    """
    exits = []
    vars = []
    exc = (None, None, None)
    try:
        for mgr in managers:
            exit = mgr.__exit__
            enter = mgr.__enter__
            vars.append(enter())
            exits.append(exit)
        yield vars
    except BaseException:
        exc = sys.exc_info()
    finally:
        while exits:
            exit = exits.pop()
            try:
                if exit(*exc):
                    exc = (None, None, None)
            except BaseException:
                exc = sys.exc_info()
        if exc != (None, None, None):
            # Don't rely on sys.exc_info() still containing
            # the right information. Another exception may
            # have been raised and caught by an exit method
            raise (exc[0], exc[1], exc[2])
