import maya.cmds as mc
from mocapx.lib.callbacks import refresh_plugin_nodes_callbacks, refresh_plugin_global_callbacks, \
    clean_plugin_nodes_callbacks, clean_plugin_global_callbacks, preload_clipreader_clips
from mocapx.lib.utils import unload_module_on_fail, clipreader_load_clip


def plugin_init():
    mc.evalDeferred(
        "import mocapx\n"
        "from mocapx.lib import plugin_init_deferred\n"
        "from mocapx.menu import create_menu\n"
        "from mocapx.shelf import create_shelf\n"
        "plugin_init_deferred()\n"
        "mocapx.mocapx_menu = create_menu()\n"
        "mocapx.mocapx_shelf = create_shelf()")


@unload_module_on_fail
def plugin_init_deferred():
    preload_clipreader_clips()
    refresh_plugin_global_callbacks()
    refresh_plugin_nodes_callbacks()


# noinspection PyUnusedLocal
def plugin_cleanup(*args, **kwargs):
    clean_plugin_nodes_callbacks()
    clean_plugin_global_callbacks()
