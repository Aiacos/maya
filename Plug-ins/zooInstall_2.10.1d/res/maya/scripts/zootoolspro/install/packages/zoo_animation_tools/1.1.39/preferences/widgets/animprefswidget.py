from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt import uiconstants
from zoo.apps.preferencesui import prefmodel
from zoo.preferences.interfaces import animinterfaces


class AnimationPreferencesWidget(prefmodel.SettingWidget):
    categoryTitle = "animation"  # The main title of the General preferences section and also side menu item

    def __init__(self, parent=None, setting=None):
        """Builds the General Section of the preferences window.

        :param parent: the parent widget
        :type parent: :class:`zoovendor.Qt.QtWidgets.QWidget`
        """
        super(AnimationPreferencesWidget, self).__init__(parent, setting)

        self.animInterface = animinterfaces.animInterface()
        self._mainLayout = elements.vBoxLayout(self,
                                               margins=(uiconstants.WINSIDEPAD,
                                                        uiconstants.WINTOPPAD,
                                                        uiconstants.WINSIDEPAD,
                                                        uiconstants.WINBOTPAD),
                                               spacing=uiconstants.SREG)
        self.studioLibraryWidget = None  # type: elements.DirectoryPathWidget
        self._currentPath = self.animInterface.studioLibraryPath()  # for revert back to current path
        self.uiLayout()  # Adds widgets to the layouts


    def uiLayout(self):
        toolTip = "Select the studio library folder path."
        self.studioLibraryWidget = elements.DirectoryPathWidget(label="Studio Library Path:",
                                                                path=self._currentPath,
                                                                parent=self,
                                                                toolTip=toolTip)
        self._mainLayout.addWidget(self.studioLibraryWidget)
        self._mainLayout.addStretch(1)


    def serialize(self):
        """ Save the current settings to the preference file, used for both Apply and Save buttons

        Automatically connected to the preferences window buttons via model.SettingWidget

        :return: Returns true if successful in saving, false otherwise
        :rtype: bool
        """
        self.animInterface.setStudioLibraryPath(self.studioLibraryWidget.path())
        self.animInterface.saveSettings()

    def revert(self):
        """Reverts to the previous settings, resets the GUI to the previously saved settings

        Automatically connected to the preferences window revert button via model.SettingWidget
        """
        self.studioLibraryWidget.setPathText(self._currentPath)
        self.serialize()
        # self._setPaths()
