import os

from zoo.preferences import prefinterface


studioLibraryPath = "studioLibraryPath"


class AnimationInterface(prefinterface.PreferenceInterface):
    id = "animation"
    _relativePath = "prefs/maya/animation.pref"

    def studioLibraryPath(self):
        """Returns the studio library folder path.

        :rtype: str
        """
        settings = self.settings()
        slPath = settings.get("settings", {}).get(studioLibraryPath, "")
        if not slPath:
            return ""
        return slPath


    def setStudioLibraryPath(self, path):
        """Sets the studio library folder path for ZooTools to use..

        :param path: The path to the studio library folder.
        :type path: str
        """
        settings = self.settings()
        settings.setdefault("settings", {})[studioLibraryPath]= os.path.normpath(path)

