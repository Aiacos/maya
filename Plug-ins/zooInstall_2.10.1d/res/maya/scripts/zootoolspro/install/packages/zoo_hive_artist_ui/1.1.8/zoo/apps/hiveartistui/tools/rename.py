import re
from functools import partial

from zoo.apps.hiveartistui import hivetool
from zoo.core.util import strutils
from zoo.libs.commands import hive
from zoo.libs.pyqt import validators
from zoo.libs.pyqt.widgets import elements


class RenameTool(hivetool.HiveTool):
    id = "renameRig"
    uiData = {"icon": "pencil", "label": "Rename Rig"}

    def execute(self):
        if self.rigExists():
            return
        m = elements.InputDialog(
            parent=self.parentWidget,
            title="Rename Rig",
            message="Enter new rig Name:",
            text=self.rigModel.name,
        )
        validator = validators.createRegexValidator("[a-zA-Z0-9_]+", self)
        m.inputEdit.setValidator(validator)

        m.show()
        m.buttons[0].clicked.connect(partial(self._onOk, m))
        # because the dialog internals call left clicked because someone is stupid and if
        # i change it to clicked who know how much breaks grrr
        m.buttons[m.default].leftClicked.connect(partial(self._onOk, m))

    def _onOk(self, dialog):
        text = dialog.inputEdit.text()
        if not text:
            return
        # Replace multiple underscores with a single underscore
        text = re.sub(r'_+', '_', text)
        if text != self.rigModel.name:
            hive.renameRig(self.rigModel.rig, str(text))

        self.requestRefresh()
        self.parentWidget.updateRigName()


class SetComponentSide(hivetool.HiveTool):
    id = "setComponentSide"
    uiData = {"icon": "solo", "label": "Set Component Side"}

    def execute(self, side, componentModel=None):
        if not self._rigModel:
            return
        model = componentModel or self.selectedComponents()[0]
        model.side = side
        self.requestRefresh()
        self.refreshComponents([model])
