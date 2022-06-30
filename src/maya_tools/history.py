"""History related utilities."""
import contextlib
import functools
import logging
from typing import Generator, Optional

from maya import cmds

__all__ = ["repeat", "undo"]

LOG = logging.getLogger(__name__)


def repeat(func):  # type: ignore
    """Decorate a function to make it repeatable.

    This means that in maya, when the shortcut ``ctrl+G`` is triggered,
    the decorate function will be executed again.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):  # type: ignore
        name = "__function_to_repeat__"
        globals()[name] = functools.partial(func, *args, **kwargs)
        cmds.repeatLast(
            addCommandLabel="{f.__module__}.{f.__name__}".format(f=func),
            addCommand='python("import {0};{0}.{1}()")'.format(__name__, name),
        )
        return func(*args, **kwargs)

    return _wrapper


@contextlib.contextmanager
def undo(name=None):
    # type: (Optional[str]) ->  Generator[None, None, None]
    """Gather all the maya commands under the same undo chunk.

    Using the maya ``cmds.undoInfo()`` command to create the chunk can be
    dangerous if used incorrectly. If a chunk is opened but never closed
    (e.g. an error occurs during execution), the maya undo list may be
    corrupted, and some features may not work properly.

    This context manager will handle the issue and like the :func:`open`
    function, will ensure that the chunk is properly close whatever happen
    during the execution of the body.

    Examples:
        First, the default behaviour of Maya. When the undo is performed,
        the last node created is correctly undone, but the first one still
        exists in the scene:

        >>> from maya import cmds
        >>> _ = cmds.file(new=True, force=True)
        >>> _ = cmds.createNode("transform", name="A")
        >>> _ = cmds.createNode("transform", name="B")
        >>> cmds.undo()
        >>> cmds.objExists("B")
        False
        >>> cmds.objExists("A")
        True

        The undo chunk allows a block of commands to be collected within
        the same undo chunk which can be undo at once:

        >>> _ = cmds.file(new=True, force=True)
        >>> with undo(name="create_transform"):
        ...     _ = cmds.createNode("transform", name="A")
        ...     _ = cmds.createNode("transform", name="B")
        >>> cmds.undoInfo(query=True, undoName=True)
        'create_transform'
        >>> cmds.undo()
        >>> cmds.objExists("B")
        False
        >>> cmds.objExists("A")
        False

    Arguments:
        name (str): The name with which the chunk can be identified.
    """
    try:
        cmds.undoInfo(chunkName=name, openChunk=True)
        yield
    finally:
        cmds.undoInfo(chunkName=name, closeChunk=True)
