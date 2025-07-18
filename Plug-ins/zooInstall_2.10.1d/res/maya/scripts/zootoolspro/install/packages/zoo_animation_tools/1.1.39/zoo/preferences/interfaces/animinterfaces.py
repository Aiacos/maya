from zoo.preferences.core import preference


def animInterface():
    """ Get the Animation preferences interface instance.

    :rtype: :class:`preferences.interface.animation.AnimationInterface`
    """

    return preference.interface("animation")


