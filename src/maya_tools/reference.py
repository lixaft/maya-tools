"""Reference utilities."""
import logging

from maya import cmds

LOG = logging.getLogger(__name__)


def remove_edits(reference, command=None):
    # type: (str, str | None) -> None
    """Remove the reference edits."""
    flags = {}
    if command is not None:
        flags["editCommand"] = command
    cmds.referenceEdit(reference, remove_edits=True, **flags)
