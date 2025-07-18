from zoovendor.Qt import QtWidgets, QtCore, QtCompat, QtGui
from zoo.libs.pyqt.models import modelutils


class TableView(QtWidgets.QTableView):
    contextMenuRequested = QtCore.Signal()
    # signal for selected rows which as copied
    copyRequested = QtCore.Signal(list)
    # signal for selected rows which as pasted
    pasteRequested = QtCore.Signal(list)

    def __init__(self, parent):
        super(TableView, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        QtCompat.setSectionResizeMode(self.verticalHeader(), QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.customContextMenuRequested.connect(self.contextMenuRequested.emit)
        self.copyPasteSupported = False

    def keyPressEvent(self, event):
        """

        :param event:
        :type event: :class;`QtCore.QKeyEvent`
        :return:
        :rtype:
        """

        model = self.model()
        if not model or not self.copyPasteSupported:
            super(TableView, self).keyPressEvent(event)
            return

        selection = self.selectionModel().selectedRows()
        if event.matches(QtGui.QKeySequence.Copy):
            self.copyRequested.emit(selection)
            event.accept()

        elif event.matches(QtGui.QKeySequence.Paste):
            self.pasteRequested.emit(selection)
        event.accept()
        # note: we don't call super here which would cause main application to copy/paste eg. maya
