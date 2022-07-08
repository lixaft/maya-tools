"""Internal utilities to manage the functions inside the package."""
import functools
import logging
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
