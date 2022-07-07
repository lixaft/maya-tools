"""Provide utilities related to plugins."""
import logging

from maya import cmds

__all__ = ["remove_unknown", "reload", "load", "unload"]

LOG = logging.getLogger(__name__)


def remove_unknown():
    # type: () -> None
    """Remove the unused plugin present in the current scene."""
    for plugin in cmds.unknownPlugin(query=True, list=True) or []:
        cmds.unknownPlugin(plugin, remove=True)
        LOG.info("Unloading unknown plugin: '%s'", plugin)


def reload(name):
    # type: (str) -> None
    """Safe reload of a plugin based on its name.

    Warning:
        During the process all the undo queue will be deleted.

    Arguments:
        name: The name of the plugin to reload.
    """
    unload(name)
    load(name)


def load(name):
    # type: (str) -> None
    """Load the given plugin.

    Argguments:
        name: The name of the plugin that should be loaded.
    """
    if not cmds.pluginInfo(name, query=True, loaded=True):
        cmds.loadPlugin(name)


def unload(name):
    # type: (str) -> None
    """Unload the given plugin.

    Warning:
        During the process all the undo queue will be deleted.

    Argguments:
        name: The name of the plugin that should be unloaded.
    """
    if cmds.pluginInfo(name, query=True, loaded=True):
        cmds.flushUndo()
        cmds.unloadPlugin(name)
