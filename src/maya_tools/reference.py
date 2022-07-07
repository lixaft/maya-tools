"""Reference utilities."""
import logging
from typing import Optional

from maya import cmds

LOG = logging.getLogger(__name__)


def remove_edits(reference, command=None):
    # type: (str, Optional[str]) -> None
    """Remove the reference edits."""
    flags = {}
    if command is not None:
        flags["editCommand"] = command
    cmds.referenceEdit(reference, remove_edits=True, **flags)
