import os
import platform


def paths_sep():
    """Returns the paths separator character for the current system platform.
    
    Returns:
        str: paths separator (';' for Windows, ':' otherwise).
    """
    return ";" if platform.system() == "Windows" else ":"


def get_icon_path(icon):
    """Searches for a valid file for the given icon in the resources paths in ADONISFX_RESOURCES env and returns it.

    Args:
        icon (str): short name of the icon file (i.e.: "adn_logo_small.png").

    Raises:
        RuntimeError: if ADONISFX_RESOURCES env is not set.
        RuntimeError: if ADONISFX_RESOURCES env is set and it is empty.
        IOError: if any file was found for the requested icon.

    Returns:
        str: full path to the icon file.
    """
    resources_path = os.getenv("ADONISFX_RESOURCES", None)
    if not resources_path:
        raise RuntimeError("[AdonisFX] Could not find icons folder: ADONISFX_RESOURCES env not set.")
    
    resources_path_list = resources_path.split(paths_sep())
    if not resources_path_list:
        raise RuntimeError("[AdonisFX] Could not find icons folder: ADONISFX_RESOURCES env is empty.")

    for p in resources_path_list:
        icon_path = os.path.join(p, icon)
        if os.path.exists(icon_path):
            return icon_path
    
    raise IOError("[AdonisFX] Could not find icon: {0}.".format(icon))
