""" Preset of cartoon_a modules building a fish character. """

from arise.data_types import preset_data

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Aquatic"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["tentacle", "aquatic", "fins", "gills", "limbs", "sea", ]
TOOL_TIP = "Cartoon fish preset."  # short explanation on module.


class CA_Fish(preset_data.PresetData):
    """Very simple class that needs no reimplementation. the only section to manually change is the variables
        above the class: TOOL_TIP, TAGS, RIG_TYPE, RIG_CATEGORY, AUTHOR, MAYA_VERSION.
    """
    sort_priority = 500

    def __init__(self, scene_ptr):
        preset_data.PresetData.__init__(self, scene_ptr=scene_ptr)
