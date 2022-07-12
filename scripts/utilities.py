"""Utilities for python scripts."""
import os
import re
import sys


def find_mayapy(version=None):
    # type: (Optional[int]) -> Optional[str]
    """Find a mayapy executable path.

    Arguments:
        version (int, optional): Specify the version of the executable that
            will be searched. By default, it returns the most recent version
            present on the system.

    Returns:
        str: The path to the mayapy executable.
    """
    path = {
        "win32": os.path.normpath("C:/Program Files/Autodesk/"),
        "darwin": os.path.normpath("/Applications/Autodesk/"),
        "linux": os.path.normpath("/usr/autodesk/"),
        "linux2": os.path.normpath("/usr/autodesk/"),
    }[sys.platform]

    if version is None:
        # Search for the most recent version of maya.
        for each in os.listdir(path):
            if not re.match(r"(M|m)aya[0-9]{4}(-x64)?", each):
                continue
            number = int(each[4:].replace("-x64", ""))
            if number > (version or 0):
                version = number

    path = os.path.join(path, "maya{}".format(version))
    if sys.platform == "darwin":
        path = os.path.join(path, "Maya.app", "Contents")
    path = os.path.join(path, "bin", "mayapy")
    if sys.platform == "win32":
        path += ".exe"

    if not os.path.exists(path):
        return None
    return path
