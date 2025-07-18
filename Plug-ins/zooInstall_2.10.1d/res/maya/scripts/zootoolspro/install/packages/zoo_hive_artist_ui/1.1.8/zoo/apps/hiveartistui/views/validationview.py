from zoovendor.Qt import QtWidgets, QtCore, QtGui

from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt import utils, uiconstants


class ValidationButton(QtWidgets.QFrame):
    recheckSignal = QtCore.Signal()
    showUISignal = QtCore.Signal()

    def __init__(self, parent=None):
        super(ValidationButton, self).__init__(parent=parent)
        mainLayout = elements.hBoxLayout(self, (0, 0, 0, 0), spacing=uiconstants.SPACING)
        toolTip = "Close the Validation Issues"
        self.closeBtn = self.rotatePosBtn = elements.styledButton("",
                                                                  "closeX",
                                                                  self,
                                                                  toolTip=toolTip,
                                                                  style=uiconstants.BTN_TRANSPARENT_BG,
                                                                  minWidth=uiconstants.BTN_W_ICN_REG)
        self.closeBtn.clicked.connect(self.hide)
        toolTip = ("Issues have been found. \n"
                   "Open the Validation Issues popup for more information.")
        self.showBtn = elements.styledButton("Show Found Issues",
                                             parent=self,
                                             toolTip=toolTip,
                                             themeUpdates=False)
        toolTip = "Recheck the Validation Issues"
        self.recheckBtn = elements.styledButton("Recheck",
                                                parent=self,
                                                icon="reload2",
                                                toolTip=toolTip,
                                                themeUpdates=False)
        self.recheckBtn.clicked.connect(self.recheckSignal.emit)
        self.showBtn.clicked.connect(self.showUISignal.emit)
        self.setMaximumHeight(utils.sizeByDpi(QtCore.QSize(20, 20)).height())
        mainLayout.addWidget(self.closeBtn, 1)
        mainLayout.addWidget(self.showBtn, 200)
        mainLayout.addWidget(self.recheckBtn, 200)

    def setValidationState(self, status):
        if status == 0:
            color = QtGui.QColor("#55ab64")
            self.showBtn.setIconByName("checkMark", colors=[
                (color.red(), color.green(), color.blue(), color.alpha())])
            self.hide()
        elif status == 1:
            color = QtGui.QColor("#ffe700")
            self.showBtn.setIconByName("warning", colors=[
                (color.red(), color.green(), color.blue(), color.alpha())])
            self.show()
        elif status == 2:
            color = QtGui.QColor("#CC0000")
            self.showBtn.setIconByName("xCircleMark2", colors=[
                (color.red(), color.green(), color.blue(), color.alpha())])
            self.show()


class ValidationView(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ValidationView, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scrollWid = QtWidgets.QWidget(self)
        self.scroll.setWidget(self.scrollWid)

        elements.vBoxLayout(self.scrollWid, (0, 0, 0, 0), spacing=10)
        mainLayout = elements.vBoxLayout(self, (0, 0, 0, 0), spacing=0)
        mainLayout.addWidget(self.scroll)
        self.resize(300, 200)
        self.shouldDisplay = False

    def reload(self, validationInfo):
        """

        :param validationInfo:
        :type validationInfo: :class:`zoo.libs.hive.base.errors.ValidationRigInfo` or None
        :return:
        :rtype:
        """
        self.shouldDisplay = False if not validationInfo else True
        layout = self.scrollWid.layout()
        utils.clearLayout(layout)
        if not self.shouldDisplay:
            return

        for info in validationInfo.issues:
            if info.status == 0:
                continue
            layout.addWidget(ValidationWidget(info, parent=self))
        verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)


class ValidationWidget(QtWidgets.QFrame):
    def __init__(self, validationInfo, parent=None):
        super(ValidationWidget, self).__init__(parent=parent)
        layout = elements.vBoxLayout(self, (uiconstants.REGPAD, uiconstants.REGPAD, uiconstants.REGPAD,
                                            uiconstants.REGPAD), spacing=uiconstants.BOTPAD)
        statusLabels = (
            "Success",
            "Warning",
            "Error"
        )
        # Create QLabel instances with HTML formatting
        title_label = QtWidgets.QLabel("<strong>{}</strong>".format(validationInfo.label))
        status_label = QtWidgets.QLabel(
            "<strong>Status:</strong> <strong style='color: red;'>{}</strong>".format(
                statusLabels[validationInfo.status]))
        body_label = QtWidgets.QLabel("<strong>Issue:</strong> {}".format(validationInfo.message))
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(status_label)
        layout.addWidget(body_label)
        self.setLayout(layout)
