# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './main_view.ui'
#
# Created: Sun Apr 15 15:55:17 2018
#      by: pyside2-uic  running on PySide2 5.9.0a1
#
# WARNING! All changes made in this file will be lost!

from zoovendor.Qt import QtCore, QtGui, QtWidgets, QtCompat


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2336, 1573)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSpacing(2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 2, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 0, 3, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setMinimumSize(QtCore.QSize(0, 0))
        self.label_19.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.gridLayout_2.addWidget(self.label_19, 1, 0, 1, 2)
        self.fontComboBox = QtWidgets.QFontComboBox(self.centralwidget)
        self.fontComboBox.setMinimumSize(QtCore.QSize(0, 0))
        self.fontComboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.fontComboBox.setObjectName("fontComboBox")
        self.gridLayout_2.addWidget(self.fontComboBox, 1, 2, 1, 1)
        self.fontComboBoxDis = QtWidgets.QFontComboBox(self.centralwidget)
        self.fontComboBoxDis.setEnabled(False)
        self.fontComboBoxDis.setMinimumSize(QtCore.QSize(0, 0))
        self.fontComboBoxDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.fontComboBoxDis.setObjectName("fontComboBoxDis")
        self.gridLayout_2.addWidget(self.fontComboBoxDis, 1, 3, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.centralwidget)
        self.label_22.setMinimumSize(QtCore.QSize(0, 0))
        self.label_22.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 2, 0, 1, 2)
        self.lineEditDis = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditDis.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditDis.sizePolicy().hasHeightForWidth())
        self.lineEditDis.setSizePolicy(sizePolicy)
        self.lineEditDis.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEditDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineEditDis.setObjectName("lineEditDis")
        self.gridLayout_2.addWidget(self.lineEditDis, 2, 3, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setMinimumSize(QtCore.QSize(0, 0))
        self.label_15.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 3, 0, 1, 2)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 3, 2, 1, 1)
        self.textEditDis = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditDis.setEnabled(False)
        self.textEditDis.setMinimumSize(QtCore.QSize(0, 0))
        self.textEditDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.textEditDis.setObjectName("textEditDis")
        self.gridLayout_2.addWidget(self.textEditDis, 3, 3, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.centralwidget)
        self.label_23.setMinimumSize(QtCore.QSize(0, 0))
        self.label_23.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.gridLayout_2.addWidget(self.label_23, 4, 0, 1, 2)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout_2.addWidget(self.plainTextEdit, 4, 2, 1, 1)
        self.plainTextEditDis = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEditDis.setEnabled(False)
        self.plainTextEditDis.setMinimumSize(QtCore.QSize(0, 0))
        self.plainTextEditDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.plainTextEditDis.setObjectName("plainTextEditDis")
        self.gridLayout_2.addWidget(self.plainTextEditDis, 4, 3, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setMinimumSize(QtCore.QSize(0, 0))
        self.label_16.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 5, 0, 1, 2)
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setMinimumSize(QtCore.QSize(0, 0))
        self.spinBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_2.addWidget(self.spinBox, 5, 2, 1, 1)
        self.spinBoxDis = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBoxDis.setEnabled(False)
        self.spinBoxDis.setMinimumSize(QtCore.QSize(0, 0))
        self.spinBoxDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.spinBoxDis.setObjectName("spinBoxDis")
        self.gridLayout_2.addWidget(self.spinBoxDis, 5, 3, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setMinimumSize(QtCore.QSize(0, 0))
        self.label_17.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 6, 0, 1, 2)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(0, 0))
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout_2.addWidget(self.doubleSpinBox, 6, 2, 1, 1)
        self.doubleSpinBoxDis = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBoxDis.setEnabled(False)
        self.doubleSpinBoxDis.setMinimumSize(QtCore.QSize(0, 0))
        self.doubleSpinBoxDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.doubleSpinBoxDis.setObjectName("doubleSpinBoxDis")
        self.gridLayout_2.addWidget(self.doubleSpinBoxDis, 6, 3, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.centralwidget)
        self.label_21.setMinimumSize(QtCore.QSize(0, 0))
        self.label_21.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.gridLayout_2.addWidget(self.label_21, 7, 0, 1, 2)
        self.timeEdit = QtWidgets.QTimeEdit(self.centralwidget)
        self.timeEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.timeEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.timeEdit.setObjectName("timeEdit")
        self.gridLayout_2.addWidget(self.timeEdit, 7, 2, 1, 1)
        self.timeEditDis = QtWidgets.QTimeEdit(self.centralwidget)
        self.timeEditDis.setEnabled(False)
        self.timeEditDis.setMinimumSize(QtCore.QSize(0, 0))
        self.timeEditDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.timeEditDis.setObjectName("timeEditDis")
        self.gridLayout_2.addWidget(self.timeEditDis, 7, 3, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.centralwidget)
        self.label_20.setMinimumSize(QtCore.QSize(0, 0))
        self.label_20.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 8, 0, 1, 2)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.dateTimeEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.gridLayout_2.addWidget(self.dateTimeEdit, 8, 2, 1, 1)
        self.dateTimeEditDis = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEditDis.setEnabled(False)
        self.dateTimeEditDis.setMinimumSize(QtCore.QSize(0, 0))
        self.dateTimeEditDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.dateTimeEditDis.setObjectName("dateTimeEditDis")
        self.gridLayout_2.addWidget(self.dateTimeEditDis, 8, 3, 1, 1)
        self.label_56 = QtWidgets.QLabel(self.centralwidget)
        self.label_56.setMinimumSize(QtCore.QSize(0, 0))
        self.label_56.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_56.setFont(font)
        self.label_56.setObjectName("label_56")
        self.gridLayout_2.addWidget(self.label_56, 9, 0, 1, 2)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.listWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.listWidget.setObjectName("listWidget")
        QtWidgets.QListWidgetItem(self.listWidget)
        QtWidgets.QListWidgetItem(self.listWidget)
        QtWidgets.QListWidgetItem(self.listWidget)
        QtWidgets.QListWidgetItem(self.listWidget)
        self.gridLayout_2.addWidget(self.listWidget, 9, 2, 1, 1)
        self.listWidgetDis = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetDis.setEnabled(False)
        self.listWidgetDis.setObjectName("listWidgetDis")
        QtWidgets.QListWidgetItem(self.listWidgetDis)
        QtWidgets.QListWidgetItem(self.listWidgetDis)
        QtWidgets.QListWidgetItem(self.listWidgetDis)
        QtWidgets.QListWidgetItem(self.listWidgetDis)
        self.gridLayout_2.addWidget(self.listWidgetDis, 9, 3, 1, 1)
        self.label_57 = QtWidgets.QLabel(self.centralwidget)
        self.label_57.setMinimumSize(QtCore.QSize(0, 0))
        self.label_57.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_57.setFont(font)
        self.label_57.setObjectName("label_57")
        self.gridLayout_2.addWidget(self.label_57, 10, 0, 1, 2)
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.treeWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.gridLayout_2.addWidget(self.treeWidget, 10, 2, 1, 1)
        self.treeWidgetDis = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidgetDis.setEnabled(False)
        self.treeWidgetDis.setObjectName("treeWidgetDis")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidgetDis)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_1)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidgetDis)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.gridLayout_2.addWidget(self.treeWidgetDis, 10, 3, 1, 1)
        self.label_58 = QtWidgets.QLabel(self.centralwidget)
        self.label_58.setMinimumSize(QtCore.QSize(0, 0))
        self.label_58.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_58.setFont(font)
        self.label_58.setObjectName("label_58")
        self.gridLayout_2.addWidget(self.label_58, 11, 0, 1, 2)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(2, 1, item)
        self.gridLayout_2.addWidget(self.tableWidget, 11, 2, 1, 1)
        self.tableWidgetDis = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetDis.setEnabled(False)
        self.tableWidgetDis.setObjectName("tableWidgetDis")
        self.tableWidgetDis.setColumnCount(2)
        self.tableWidgetDis.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDis.setItem(2, 1, item)
        self.gridLayout_2.addWidget(self.tableWidgetDis, 11, 3, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_27.setFont(font)
        self.label_27.setObjectName("label_27")
        self.gridLayout_2.addWidget(self.label_27, 12, 0, 1, 2)
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setObjectName("listView")
        self.gridLayout_2.addWidget(self.listView, 12, 2, 1, 1)
        self.listViewDis = QtWidgets.QListView(self.centralwidget)
        self.listViewDis.setEnabled(False)
        self.listViewDis.setObjectName("listViewDis")
        self.gridLayout_2.addWidget(self.listViewDis, 12, 3, 1, 1)
        self.label_59 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_59.setFont(font)
        self.label_59.setObjectName("label_59")
        self.gridLayout_2.addWidget(self.label_59, 13, 0, 1, 2)
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setObjectName("treeView")
        self.gridLayout_2.addWidget(self.treeView, 13, 2, 1, 1)
        self.treeViewDis = QtWidgets.QTreeView(self.centralwidget)
        self.treeViewDis.setEnabled(False)
        self.treeViewDis.setObjectName("treeViewDis")
        self.gridLayout_2.addWidget(self.treeViewDis, 13, 3, 1, 1)
        self.label_62 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_62.setFont(font)
        self.label_62.setObjectName("label_62")
        self.gridLayout_2.addWidget(self.label_62, 14, 0, 1, 2)
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.gridLayout_2.addWidget(self.tableView, 14, 2, 1, 1)
        self.tableViewDis = QtWidgets.QTableView(self.centralwidget)
        self.tableViewDis.setEnabled(False)
        self.tableViewDis.setObjectName("tableViewDis")
        self.gridLayout_2.addWidget(self.tableViewDis, 14, 3, 1, 1)
        self.label_63 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_63.setFont(font)
        self.label_63.setObjectName("label_63")
        self.gridLayout_2.addWidget(self.label_63, 15, 0, 1, 2)
        self.columnView = QtWidgets.QColumnView(self.centralwidget)
        self.columnView.setObjectName("columnView")
        self.gridLayout_2.addWidget(self.columnView, 15, 2, 1, 1)
        self.columnViewDis = QtWidgets.QColumnView(self.centralwidget)
        self.columnViewDis.setEnabled(False)
        self.columnViewDis.setObjectName("columnViewDis")
        self.gridLayout_2.addWidget(self.columnViewDis, 15, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            120, 6, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_2.addItem(spacerItem, 16, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            177, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_2.addItem(spacerItem1, 16, 1, 1, 2)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.enabledLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.enabledLabel.setFont(font)
        self.enabledLabel.setObjectName("enabledLabel")
        self.gridLayout.addWidget(self.enabledLabel, 0, 1, 1, 1)
        self.disabledLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.disabledLabel.setFont(font)
        self.disabledLabel.setObjectName("disabledLabel")
        self.gridLayout.addWidget(self.disabledLabel, 0, 2, 1, 1)
        self.pushbtn_1 = QtWidgets.QLabel(self.centralwidget)
        self.pushbtn_1.setMinimumSize(QtCore.QSize(0, 0))
        self.pushbtn_1.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.pushbtn_1.setFont(font)
        self.pushbtn_1.setObjectName("pushbtn_1")
        self.gridLayout.addWidget(self.pushbtn_1, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 1, 1, 1)
        self.pushButtonDis = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonDis.setEnabled(False)
        self.pushButtonDis.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButtonDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pushButtonDis.setDefault(False)
        self.pushButtonDis.setObjectName("pushButtonDis")
        self.gridLayout.addWidget(self.pushButtonDis, 1, 2, 1, 1)
        self.buttonBtnCheckable = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.buttonBtnCheckable.setFont(font)
        self.buttonBtnCheckable.setObjectName("buttonBtnCheckable")
        self.gridLayout.addWidget(self.buttonBtnCheckable, 2, 0, 1, 1)
        self.pushButtonUnchecked = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonUnchecked.setCheckable(True)
        self.pushButtonUnchecked.setObjectName("pushButtonUnchecked")
        self.gridLayout.addWidget(self.pushButtonUnchecked, 2, 1, 1, 1)
        self.pushButtonUncheckedDis = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonUncheckedDis.setEnabled(False)
        self.pushButtonUncheckedDis.setCheckable(True)
        self.pushButtonUncheckedDis.setObjectName("pushButtonUncheckedDis")
        self.gridLayout.addWidget(self.pushButtonUncheckedDis, 2, 2, 1, 1)
        self.toolbutton = QtWidgets.QLabel(self.centralwidget)
        self.toolbutton.setMinimumSize(QtCore.QSize(0, 0))
        self.toolbutton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.toolbutton.setFont(font)
        self.toolbutton.setObjectName("toolbutton")
        self.gridLayout.addWidget(self.toolbutton, 3, 0, 1, 1)
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setMinimumSize(QtCore.QSize(0, 0))
        self.toolButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 3, 1, 1, 1)
        self.toolButtonDis = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonDis.setEnabled(False)
        self.toolButtonDis.setMinimumSize(QtCore.QSize(0, 0))
        self.toolButtonDis.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.toolButtonDis.setObjectName("toolButtonDis")
        self.gridLayout.addWidget(self.toolButtonDis, 3, 2, 1, 1)
        self.radiobutton = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.radiobutton.setFont(font)
        self.radiobutton.setObjectName("radiobutton")
        self.gridLayout.addWidget(self.radiobutton, 4, 0, 1, 1)
        self.radioButtonChecked = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonChecked.setChecked(True)
        self.radioButtonChecked.setAutoExclusive(False)
        self.radioButtonChecked.setObjectName("radioButtonChecked")
        self.gridLayout.addWidget(self.radioButtonChecked, 4, 1, 1, 1)
        self.radioButtonCheckedDis = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonCheckedDis.setEnabled(False)
        self.radioButtonCheckedDis.setChecked(True)
        self.radioButtonCheckedDis.setAutoExclusive(False)
        self.radioButtonCheckedDis.setObjectName("radioButtonCheckedDis")
        self.gridLayout.addWidget(self.radioButtonCheckedDis, 4, 2, 1, 1)
        self.checkbox = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.checkbox.setFont(font)
        self.checkbox.setObjectName("checkbox")
        self.gridLayout.addWidget(self.checkbox, 5, 0, 1, 1)
        self.checkBoxChecked = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBoxChecked.setChecked(True)
        self.checkBoxChecked.setObjectName("checkBoxChecked")
        self.gridLayout.addWidget(self.checkBoxChecked, 5, 1, 1, 1)
        self.checkBoxCheckedDis = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBoxCheckedDis.setEnabled(False)
        self.checkBoxCheckedDis.setChecked(True)
        self.checkBoxCheckedDis.setObjectName("checkBoxCheckedDis")
        self.gridLayout.addWidget(self.checkBoxCheckedDis, 5, 2, 1, 1)
        self.commandLinkBtn = QtWidgets.QLabel(self.centralwidget)
        self.commandLinkBtn.setMinimumSize(QtCore.QSize(0, 0))
        self.commandLinkBtn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.commandLinkBtn.setFont(font)
        self.commandLinkBtn.setObjectName("commandLinkBtn")
        self.gridLayout.addWidget(self.commandLinkBtn, 6, 0, 1, 1)
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.centralwidget)
        self.commandLinkButton.setMinimumSize(QtCore.QSize(0, 0))
        self.commandLinkButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.gridLayout.addWidget(self.commandLinkButton, 6, 1, 1, 1)
        self.commandLinkButtonDIs = QtWidgets.QCommandLinkButton(self.centralwidget)
        self.commandLinkButtonDIs.setEnabled(False)
        self.commandLinkButtonDIs.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.commandLinkButtonDIs.setObjectName("commandLinkButtonDIs")
        self.gridLayout.addWidget(self.commandLinkButtonDIs, 6, 2, 1, 1)
        self.buttonBox_2 = QtWidgets.QLabel(self.centralwidget)
        self.buttonBox_2.setMinimumSize(QtCore.QSize(0, 0))
        self.buttonBox_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.buttonBox_2.setFont(font)
        self.buttonBox_2.setObjectName("buttonBox_2")
        self.gridLayout.addWidget(self.buttonBox_2, 7, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setMinimumSize(QtCore.QSize(0, 0))
        self.buttonBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 7, 1, 1, 1)
        self.buttonBoxDis = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBoxDis.setEnabled(False)
        self.buttonBoxDis.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBoxDis.setObjectName("buttonBoxDis")
        self.gridLayout.addWidget(self.buttonBoxDis, 7, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setMinimumSize(QtCore.QSize(0, 0))
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 8, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setMinimumSize(QtCore.QSize(0, 0))
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 8, 1, 1, 1)
        self.label_79 = QtWidgets.QLabel(self.centralwidget)
        self.label_79.setEnabled(False)
        self.label_79.setObjectName("label_79")
        self.gridLayout.addWidget(self.label_79, 8, 2, 1, 1)
        self.label_131 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_131.setFont(font)
        self.label_131.setObjectName("label_131")
        self.gridLayout.addWidget(self.label_131, 9, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_43 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_43.setObjectName("gridLayout_43")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setObjectName("label_13")
        self.gridLayout_43.addWidget(self.label_13, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame_2, 9, 1, 1, 1)
        self.frameDis_2 = QtWidgets.QFrame(self.centralwidget)
        self.frameDis_2.setEnabled(False)
        self.frameDis_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameDis_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameDis_2.setObjectName("frameDis_2")
        self.gridLayout_40 = QtWidgets.QGridLayout(self.frameDis_2)
        self.gridLayout_40.setObjectName("gridLayout_40")
        self.label_14 = QtWidgets.QLabel(self.frameDis_2)
        self.label_14.setObjectName("label_14")
        self.gridLayout_40.addWidget(self.label_14, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frameDis_2, 9, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setMinimumSize(QtCore.QSize(0, 0))
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 10, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setMinimumSize(QtCore.QSize(0, 0))
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 10, 1, 1, 1)
        self.textBrowserDis = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowserDis.setEnabled(False)
        self.textBrowserDis.setObjectName("textBrowserDis")
        self.gridLayout.addWidget(self.textBrowserDis, 10, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setMinimumSize(QtCore.QSize(0, 0))
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 11, 0, 1, 1)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setMinimumSize(QtCore.QSize(0, 0))
        self.graphicsView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 11, 1, 1, 1)
        self.graphicsViewDis = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsViewDis.setEnabled(False)
        self.graphicsViewDis.setObjectName("graphicsViewDis")
        self.gridLayout.addWidget(self.graphicsViewDis, 11, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setMinimumSize(QtCore.QSize(0, 0))
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 12, 0, 1, 1)
        self.calendarWidget = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.calendarWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.calendarWidget.setObjectName("calendarWidget")
        self.gridLayout.addWidget(self.calendarWidget, 12, 1, 1, 1)
        self.calendarWidgetDis = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarWidgetDis.setEnabled(False)
        self.calendarWidgetDis.setObjectName("calendarWidgetDis")
        self.gridLayout.addWidget(self.calendarWidgetDis, 12, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setMinimumSize(QtCore.QSize(0, 0))
        self.label_7.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 13, 0, 1, 1)
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setMinimumSize(QtCore.QSize(0, 0))
        self.lcdNumber.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lcdNumber.setObjectName("lcdNumber")
        self.gridLayout.addWidget(self.lcdNumber, 13, 1, 1, 1)
        self.lcdNumberDis = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumberDis.setEnabled(False)
        self.lcdNumberDis.setObjectName("lcdNumberDis")
        self.gridLayout.addWidget(self.lcdNumberDis, 13, 2, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setMinimumSize(QtCore.QSize(0, 0))
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 14, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 0))
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 14, 1, 1, 1)
        self.progressBarDis = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBarDis.setEnabled(False)
        self.progressBarDis.setProperty("value", 24)
        self.progressBarDis.setObjectName("progressBarDis")
        self.gridLayout.addWidget(self.progressBarDis, 14, 2, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setMinimumSize(QtCore.QSize(0, 0))
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 15, 0, 1, 1)
        self.lineH = QtWidgets.QFrame(self.centralwidget)
        self.lineH.setMinimumSize(QtCore.QSize(0, 0))
        self.lineH.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineH.setFrameShape(QtWidgets.QFrame.HLine)
        self.lineH.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineH.setObjectName("lineH")
        self.gridLayout.addWidget(self.lineH, 15, 1, 1, 1)
        self.lineHDis = QtWidgets.QFrame(self.centralwidget)
        self.lineHDis.setEnabled(False)
        self.lineHDis.setFrameShape(QtWidgets.QFrame.HLine)
        self.lineHDis.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineHDis.setObjectName("lineHDis")
        self.gridLayout.addWidget(self.lineHDis, 15, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setMinimumSize(QtCore.QSize(0, 0))
        self.label_10.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 16, 0, 1, 1)
        self.lineV = QtWidgets.QFrame(self.centralwidget)
        self.lineV.setMinimumSize(QtCore.QSize(0, 50))
        self.lineV.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineV.setFrameShape(QtWidgets.QFrame.VLine)
        self.lineV.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineV.setObjectName("lineV")
        self.gridLayout.addWidget(self.lineV, 16, 1, 1, 1)
        self.lineVDis = QtWidgets.QFrame(self.centralwidget)
        self.lineVDis.setEnabled(False)
        self.lineVDis.setMinimumSize(QtCore.QSize(0, 50))
        self.lineVDis.setFrameShape(QtWidgets.QFrame.VLine)
        self.lineVDis.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lineVDis.setObjectName("lineVDis")
        self.gridLayout.addWidget(self.lineVDis, 16, 2, 1, 1)
        self.label_127 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_127.setFont(font)
        self.label_127.setObjectName("label_127")
        self.gridLayout.addWidget(self.label_127, 17, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout_7.addWidget(self.label_11, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 17, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 17, 2, 1, 1)
        self.label_128 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_128.setFont(font)
        self.label_128.setObjectName("label_128")
        self.gridLayout.addWidget(self.label_128, 18, 0, 1, 1)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 463, 269))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_70 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_70.setObjectName("label_70")
        self.verticalLayout_14.addWidget(self.label_70)
        self.label_71 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_71.setObjectName("label_71")
        self.verticalLayout_14.addWidget(self.label_71)
        self.label_76 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_76.setObjectName("label_76")
        self.verticalLayout_14.addWidget(self.label_76)
        self.label_75 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_75.setObjectName("label_75")
        self.verticalLayout_14.addWidget(self.label_75)
        self.label_77 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_77.setObjectName("label_77")
        self.verticalLayout_14.addWidget(self.label_77)
        self.label_78 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_78.setObjectName("label_78")
        self.verticalLayout_14.addWidget(self.label_78)
        self.label_80 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_80.setObjectName("label_80")
        self.verticalLayout_14.addWidget(self.label_80)
        self.label_81 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_81.setObjectName("label_81")
        self.verticalLayout_14.addWidget(self.label_81)
        self.label_82 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_82.setObjectName("label_82")
        self.verticalLayout_14.addWidget(self.label_82)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout.addWidget(self.scrollArea_2, 18, 1, 1, 1)
        self.scrollAreaDis_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollAreaDis_2.setEnabled(False)
        self.scrollAreaDis_2.setWidgetResizable(True)
        self.scrollAreaDis_2.setObjectName("scrollAreaDis_2")
        self.scrollAreaWidgetContentsDis_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContentsDis_2.setGeometry(QtCore.QRect(0, 0, 462, 269))
        self.scrollAreaWidgetContentsDis_2.setObjectName(
            "scrollAreaWidgetContentsDis_2"
        )
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContentsDis_2
        )
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_115 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_115.setObjectName("label_115")
        self.verticalLayout_13.addWidget(self.label_115)
        self.label_116 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_116.setObjectName("label_116")
        self.verticalLayout_13.addWidget(self.label_116)
        self.label_117 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_117.setObjectName("label_117")
        self.verticalLayout_13.addWidget(self.label_117)
        self.label_118 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_118.setObjectName("label_118")
        self.verticalLayout_13.addWidget(self.label_118)
        self.label_119 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_119.setObjectName("label_119")
        self.verticalLayout_13.addWidget(self.label_119)
        self.label_120 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_120.setObjectName("label_120")
        self.verticalLayout_13.addWidget(self.label_120)
        self.label_121 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_121.setObjectName("label_121")
        self.verticalLayout_13.addWidget(self.label_121)
        self.label_122 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_122.setObjectName("label_122")
        self.verticalLayout_13.addWidget(self.label_122)
        self.label_123 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_123.setObjectName("label_123")
        self.verticalLayout_13.addWidget(self.label_123)
        self.scrollAreaDis_2.setWidget(self.scrollAreaWidgetContentsDis_2)
        self.gridLayout.addWidget(self.scrollAreaDis_2, 18, 2, 1, 1)
        self.label_129 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        QtCompat.QFont.setWeight(font, 75)
        font.setBold(True)
        self.label_129.setFont(font)
        self.label_129.setObjectName("label_129")
        self.gridLayout.addWidget(self.label_129, 19, 0, 1, 1)
        self.toolBox_2 = QtWidgets.QToolBox(self.centralwidget)
        self.toolBox_2.setObjectName("toolBox_2")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 491, 105))
        self.page_3.setObjectName("page_3")
        self.gridLayout_41 = QtWidgets.QGridLayout(self.page_3)
        self.gridLayout_41.setObjectName("gridLayout_41")
        self.label_60 = QtWidgets.QLabel(self.page_3)
        self.label_60.setObjectName("label_60")
        self.gridLayout_41.addWidget(self.label_60, 2, 0, 1, 1)
        self.toolBox_2.addItem(self.page_3, "")
        self.page_8 = QtWidgets.QWidget()
        self.page_8.setGeometry(QtCore.QRect(0, 0, 484, 105))
        self.page_8.setObjectName("page_8")
        self.gridLayout_42 = QtWidgets.QGridLayout(self.page_8)
        self.gridLayout_42.setObjectName("gridLayout_42")
        self.label_61 = QtWidgets.QLabel(self.page_8)
        self.label_61.setObjectName("label_61")
        self.gridLayout_42.addWidget(self.label_61, 0, 0, 1, 1)
        self.toolBox_2.addItem(self.page_8, "")
        self.gridLayout.addWidget(self.toolBox_2, 19, 1, 1, 1)
        self.toolBoxDis_2 = QtWidgets.QToolBox(self.centralwidget)
        self.toolBoxDis_2.setEnabled(False)
        self.toolBoxDis_2.setObjectName("toolBoxDis_2")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setGeometry(QtCore.QRect(0, 0, 490, 105))
        self.page_6.setObjectName("page_6")
        self.gridLayout_29 = QtWidgets.QGridLayout(self.page_6)
        self.gridLayout_29.setObjectName("gridLayout_29")
        self.label_109 = QtWidgets.QLabel(self.page_6)
        self.label_109.setObjectName("label_109")
        self.gridLayout_29.addWidget(self.label_109, 0, 0, 1, 1)
        self.toolBoxDis_2.addItem(self.page_6, "")
        self.page_7 = QtWidgets.QWidget()
        self.page_7.setGeometry(QtCore.QRect(0, 0, 484, 105))
        self.page_7.setObjectName("page_7")
        self.gridLayout_34 = QtWidgets.QGridLayout(self.page_7)
        self.gridLayout_34.setObjectName("gridLayout_34")
        self.label_110 = QtWidgets.QLabel(self.page_7)
        self.label_110.setObjectName("label_110")
        self.gridLayout_34.addWidget(self.label_110, 0, 0, 1, 1)
        self.toolBoxDis_2.addItem(self.page_7, "")
        self.gridLayout.addWidget(self.toolBoxDis_2, 19, 2, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2336, 31))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAction = QtWidgets.QAction(MainWindow)
        self.actionAction.setCheckable(False)
        self.actionAction.setObjectName("actionAction")
        self.actionCheckable_action = QtWidgets.QAction(MainWindow)
        self.actionCheckable_action.setCheckable(True)
        self.actionCheckable_action.setChecked(True)
        self.actionCheckable_action.setObjectName("actionCheckable_action")
        self.menuMenu.addAction(self.actionAction)
        self.menuMenu.addAction(self.actionCheckable_action)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.toolBox_2.setCurrentIndex(0)
        self.toolBoxDis_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1)
        )
        self.label.setText(
            QtWidgets.QApplication.translate("MainWindow", "Enabled", None, -1)
        )
        self.label_18.setText(
            QtWidgets.QApplication.translate("MainWindow", "Disabled", None, -1)
        )
        self.label_19.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_19.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_19.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_19.setText(
            QtWidgets.QApplication.translate("MainWindow", "FontComboBox", None, -1)
        )
        self.fontComboBox.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.fontComboBox.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.fontComboBox.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.fontComboBoxDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.fontComboBoxDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.fontComboBoxDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_22.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_22.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_22.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_22.setText(
            QtWidgets.QApplication.translate("MainWindow", "LineEdit", None, -1)
        )
        self.lineEditDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.lineEditDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.lineEditDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.lineEditDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "LineEdit", None, -1)
        )
        self.label_15.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_15.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_15.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_15.setText(
            QtWidgets.QApplication.translate("MainWindow", "TextEdit", None, -1)
        )
        self.textEdit.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.textEdit.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.textEdit.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.textEdit.setHtml(
            QtWidgets.QApplication.translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Cantarell\'; font-size:11pt;">TextEdit</span></p></body></html>',
                None,
                -1,
            )
        )
        self.textEditDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.textEditDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.textEditDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.textEditDis.setHtml(
            QtWidgets.QApplication.translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Cantarell\'; font-size:11pt;">TextEdit</span></p></body></html>',
                None,
                -1,
            )
        )
        self.label_23.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_23.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_23.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_23.setText(
            QtWidgets.QApplication.translate("MainWindow", "PlainTextEdit", None, -1)
        )
        self.plainTextEdit.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.plainTextEdit.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.plainTextEdit.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.plainTextEdit.setPlainText(
            QtWidgets.QApplication.translate("MainWindow", "PlainTextEdit", None, -1)
        )
        self.plainTextEditDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.plainTextEditDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.plainTextEditDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.plainTextEditDis.setPlainText(
            QtWidgets.QApplication.translate("MainWindow", "PlainTextEdit", None, -1)
        )
        self.label_16.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_16.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_16.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_16.setText(
            QtWidgets.QApplication.translate("MainWindow", "SpinBox", None, -1)
        )
        self.spinBox.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.spinBox.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.spinBox.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.spinBoxDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.spinBoxDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.spinBoxDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_17.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_17.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_17.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_17.setText(
            QtWidgets.QApplication.translate("MainWindow", "DoubleSpinBox", None, -1)
        )
        self.doubleSpinBox.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.doubleSpinBox.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.doubleSpinBox.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.doubleSpinBoxDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.doubleSpinBoxDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.doubleSpinBoxDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_21.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_21.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_21.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_21.setText(
            QtWidgets.QApplication.translate("MainWindow", "TimeEdit", None, -1)
        )
        self.timeEdit.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.timeEdit.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.timeEdit.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.timeEditDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.timeEditDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.timeEditDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_20.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_20.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_20.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_20.setText(
            QtWidgets.QApplication.translate("MainWindow", "TimeDateEdit", None, -1)
        )
        self.dateTimeEdit.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.dateTimeEdit.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.dateTimeEdit.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.dateTimeEditDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.dateTimeEditDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.dateTimeEditDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_56.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_56.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_56.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_56.setText(
            QtWidgets.QApplication.translate("MainWindow", "ListWidget", None, -1)
        )
        self.listWidget.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.listWidget.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.listWidget.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        self.listWidget.item(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidget.item(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidget.item(2).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidget.item(3).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidget.setSortingEnabled(__sortingEnabled)
        __sortingEnabled = self.listWidgetDis.isSortingEnabled()
        self.listWidgetDis.setSortingEnabled(False)
        self.listWidgetDis.item(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidgetDis.item(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidgetDis.item(2).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidgetDis.item(3).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.listWidgetDis.setSortingEnabled(__sortingEnabled)
        self.label_57.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_57.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_57.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_57.setText(
            QtWidgets.QApplication.translate("MainWindow", "TreeWidget", None, -1)
        )
        self.treeWidget.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.treeWidget.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.treeWidget.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        self.treeWidget.headerItem().setText(
            1, QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.treeWidget.topLevelItem(0).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidget.topLevelItem(0).child(0).setText(
            1, QtWidgets.QApplication.translate("MainWindow", "Test", None, -1)
        )
        self.treeWidget.topLevelItem(0).child(0).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidget.topLevelItem(1).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.treeWidget.topLevelItem(1).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.treeWidgetDis.setSortingEnabled(True)
        self.treeWidgetDis.headerItem().setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        self.treeWidgetDis.headerItem().setText(
            1, QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        __sortingEnabled = self.treeWidgetDis.isSortingEnabled()
        self.treeWidgetDis.setSortingEnabled(False)
        self.treeWidgetDis.topLevelItem(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.treeWidgetDis.topLevelItem(0).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidgetDis.topLevelItem(0).child(0).setText(
            1, QtWidgets.QApplication.translate("MainWindow", "Test", None, -1)
        )
        self.treeWidgetDis.topLevelItem(0).child(0).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidgetDis.topLevelItem(1).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Item", None, -1)
        )
        self.treeWidgetDis.topLevelItem(1).child(0).setText(
            0, QtWidgets.QApplication.translate("MainWindow", "New Subitem", None, -1)
        )
        self.treeWidgetDis.setSortingEnabled(__sortingEnabled)
        self.label_58.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_58.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_58.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_58.setText(
            QtWidgets.QApplication.translate("MainWindow", "TableWidget", None, -1)
        )
        self.tableWidget.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.tableWidget.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.tableWidget.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.tableWidget.verticalHeaderItem(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidget.verticalHeaderItem(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidget.verticalHeaderItem(2).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidget.horizontalHeaderItem(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        self.tableWidget.horizontalHeaderItem(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.item(0, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "1.23", None, -1)
        )
        self.tableWidget.item(0, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Hello", None, -1)
        )
        self.tableWidget.item(1, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "1,45", None, -1)
        )
        self.tableWidget.item(1, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Olá", None, -1)
        )
        self.tableWidget.item(2, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "12/12/2012", None, -1)
        )
        self.tableWidget.item(2, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Oui", None, -1)
        )
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.tableWidgetDis.verticalHeaderItem(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidgetDis.verticalHeaderItem(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidgetDis.verticalHeaderItem(2).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Row", None, -1)
        )
        self.tableWidgetDis.horizontalHeaderItem(0).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        self.tableWidgetDis.horizontalHeaderItem(1).setText(
            QtWidgets.QApplication.translate("MainWindow", "New Column", None, -1)
        )
        __sortingEnabled = self.tableWidgetDis.isSortingEnabled()
        self.tableWidgetDis.setSortingEnabled(False)
        self.tableWidgetDis.item(0, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "1.23", None, -1)
        )
        self.tableWidgetDis.item(0, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Hello", None, -1)
        )
        self.tableWidgetDis.item(1, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "1,45", None, -1)
        )
        self.tableWidgetDis.item(1, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Olá", None, -1)
        )
        self.tableWidgetDis.item(2, 0).setText(
            QtWidgets.QApplication.translate("MainWindow", "12/12/2012", None, -1)
        )
        self.tableWidgetDis.item(2, 1).setText(
            QtWidgets.QApplication.translate("MainWindow", "Oui", None, -1)
        )
        self.tableWidgetDis.setSortingEnabled(__sortingEnabled)
        self.label_27.setText(
            QtWidgets.QApplication.translate("MainWindow", "ListView", None, -1)
        )
        self.label_59.setText(
            QtWidgets.QApplication.translate("MainWindow", "TreeView", None, -1)
        )
        self.label_62.setText(
            QtWidgets.QApplication.translate("MainWindow", "TableView", None, -1)
        )
        self.label_63.setText(
            QtWidgets.QApplication.translate("MainWindow", "ColunmView", None, -1)
        )
        self.enabledLabel.setText(
            QtWidgets.QApplication.translate("MainWindow", "Enabled", None, -1)
        )
        self.disabledLabel.setText(
            QtWidgets.QApplication.translate("MainWindow", "Disabled", None, -1)
        )
        self.pushbtn_1.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.pushbtn_1.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.pushbtn_1.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.pushbtn_1.setText(
            QtWidgets.QApplication.translate("MainWindow", "PushButton", None, -1)
        )
        self.pushButton.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.pushButton.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.pushButton.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.pushButton.setText(
            QtWidgets.QApplication.translate("MainWindow", "OK", None, -1)
        )
        self.pushButtonDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.pushButtonDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.pushButtonDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.pushButtonDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "OK", None, -1)
        )
        self.buttonBtnCheckable.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "PushButton checkable", None, -1
            )
        )
        self.pushButtonUnchecked.setText(
            QtWidgets.QApplication.translate("MainWindow", "checkable", None, -1)
        )
        self.pushButtonUncheckedDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "checkable", None, -1)
        )
        self.toolbutton.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.toolbutton.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.toolbutton.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.toolbutton.setText(
            QtWidgets.QApplication.translate("MainWindow", "ToolButton", None, -1)
        )
        self.toolButton.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.toolButton.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.toolButton.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.toolButton.setText(
            QtWidgets.QApplication.translate("MainWindow", "Tool", None, -1)
        )
        self.toolButtonDis.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.toolButtonDis.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.toolButtonDis.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.toolButtonDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "Tool", None, -1)
        )
        self.radiobutton.setText(
            QtWidgets.QApplication.translate("MainWindow", "RadioButton", None, -1)
        )
        self.radioButtonChecked.setText(
            QtWidgets.QApplication.translate("MainWindow", "Checked", None, -1)
        )
        self.radioButtonCheckedDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "Checked", None, -1)
        )
        self.checkbox.setText(
            QtWidgets.QApplication.translate("MainWindow", "CheckBox", None, -1)
        )
        self.checkBoxChecked.setText(
            QtWidgets.QApplication.translate("MainWindow", "Checked", None, -1)
        )
        self.checkBoxCheckedDis.setText(
            QtWidgets.QApplication.translate("MainWindow", "Checked", None, -1)
        )
        self.commandLinkBtn.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.commandLinkBtn.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.commandLinkBtn.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.commandLinkBtn.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "CommandLinkButton", None, -1
            )
        )
        self.commandLinkButton.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.commandLinkButton.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.commandLinkButton.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.commandLinkButton.setText(
            QtWidgets.QApplication.translate("MainWindow", "Command", None, -1)
        )
        self.commandLinkButtonDIs.setText(
            QtWidgets.QApplication.translate("MainWindow", "Command", None, -1)
        )
        self.buttonBox_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.buttonBox_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.buttonBox_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.buttonBox_2.setText(
            QtWidgets.QApplication.translate("MainWindow", "ButtonBox", None, -1)
        )
        self.buttonBox.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.buttonBox.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.buttonBox.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_3.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_3.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_3.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_3.setText(
            QtWidgets.QApplication.translate("MainWindow", "Label", None, -1)
        )
        self.label_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_2.setText(
            QtWidgets.QApplication.translate("MainWindow", "Testing", None, -1)
        )
        self.label_79.setText(
            QtWidgets.QApplication.translate("MainWindow", "Testing", None, -1)
        )
        self.label_131.setText(
            QtWidgets.QApplication.translate("MainWindow", "Frame", None, -1)
        )
        self.frame_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.frame_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.frame_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_13.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_13.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_13.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_13.setText(
            QtWidgets.QApplication.translate("MainWindow", "Inside Frame", None, -1)
        )
        self.frameDis_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.frameDis_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.frameDis_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_14.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_14.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_14.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_14.setText(
            QtWidgets.QApplication.translate("MainWindow", "Inside Frame", None, -1)
        )
        self.label_4.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_4.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_4.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_4.setText(
            QtWidgets.QApplication.translate("MainWindow", "TextBrowser", None, -1)
        )
        self.textBrowser.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.textBrowser.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.textBrowser.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.textBrowser.setHtml(
            QtWidgets.QApplication.translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Cantarell\'; font-size:11pt;">Text browser</span></p></body></html>',
                None,
                -1,
            )
        )
        self.textBrowserDis.setHtml(
            QtWidgets.QApplication.translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Cantarell\'; font-size:11pt;">Text browser</span></p>\n'
                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Cantarell'; font-size:11pt;\"><br /></p></body></html>",
                None,
                -1,
            )
        )
        self.label_5.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_5.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_5.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_5.setText(
            QtWidgets.QApplication.translate("MainWindow", "GraphicsView", None, -1)
        )
        self.graphicsView.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.graphicsView.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.graphicsView.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_6.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_6.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_6.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_6.setText(
            QtWidgets.QApplication.translate("MainWindow", "CalendarWidget", None, -1)
        )
        self.calendarWidget.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.calendarWidget.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.calendarWidget.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_7.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_7.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_7.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_7.setText(
            QtWidgets.QApplication.translate("MainWindow", "LCDNumber", None, -1)
        )
        self.lcdNumber.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.lcdNumber.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.lcdNumber.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_8.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_8.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_8.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_8.setText(
            QtWidgets.QApplication.translate("MainWindow", "ProgressBar", None, -1)
        )
        self.progressBar.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.progressBar.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.progressBar.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_9.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_9.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_9.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_9.setText(
            QtWidgets.QApplication.translate("MainWindow", "Line - H", None, -1)
        )
        self.lineH.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.lineH.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.lineH.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_10.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_10.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_10.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_10.setText(
            QtWidgets.QApplication.translate("MainWindow", "Line - V", None, -1)
        )
        self.lineV.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.lineV.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.lineV.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_127.setText(
            QtWidgets.QApplication.translate("MainWindow", "GroupBox", None, -1)
        )
        self.groupBox_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.groupBox_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.groupBox_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.groupBox_2.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "GroupBox", None, -1)
        )
        self.label_11.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_11.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_11.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_11.setText(
            QtWidgets.QApplication.translate("MainWindow", "Inside GroupBox", None, -1)
        )
        self.label_12.setText(
            QtWidgets.QApplication.translate("MainWindow", "Inside GroupBox", None, -1)
        )
        self.label_128.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.scrollArea_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.scrollArea_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.scrollArea_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_70.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_70.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_70.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_70.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_71.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_71.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_71.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_71.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea ", None, -1)
        )
        self.label_76.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_76.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_76.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_76.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_75.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_75.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_75.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_75.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea ", None, -1
            )
        )
        self.label_77.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_77.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_77.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_77.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_78.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_78.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_78.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_78.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_80.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_80.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_80.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_80.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_81.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_81.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_81.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_81.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_82.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_82.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_82.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_82.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.scrollAreaDis_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.scrollAreaDis_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.scrollAreaDis_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_115.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_115.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_115.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_115.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_116.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_116.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_116.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_116.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea ", None, -1)
        )
        self.label_117.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_117.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_117.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_117.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea ", None, -1
            )
        )
        self.label_118.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_118.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_118.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_118.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_119.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_119.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_119.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_119.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_120.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_120.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_120.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_120.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_121.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_121.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_121.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_121.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_122.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_122.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_122.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_122.setText(
            QtWidgets.QApplication.translate("MainWindow", "ScroolArea", None, -1)
        )
        self.label_123.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_123.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_123.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_123.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ScroolArea", None, -1
            )
        )
        self.label_129.setText(
            QtWidgets.QApplication.translate("MainWindow", "ToolBox", None, -1)
        )
        self.toolBox_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.toolBox_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.toolBox_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_60.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ToolBox Page 1", None, -1
            )
        )
        self.toolBox_2.setItemText(
            self.toolBox_2.indexOf(self.page_3),
            QtWidgets.QApplication.translate("MainWindow", "Page 1", None, -1),
        )
        self.label_61.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_61.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_61.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_61.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ToolBox Page 2", None, -1
            )
        )
        self.toolBox_2.setItemText(
            self.toolBox_2.indexOf(self.page_8),
            QtWidgets.QApplication.translate("MainWindow", "Page 2", None, -1),
        )
        self.toolBoxDis_2.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.toolBoxDis_2.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.toolBoxDis_2.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_109.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ToolBox Page 1", None, -1
            )
        )
        self.toolBoxDis_2.setItemText(
            self.toolBoxDis_2.indexOf(self.page_6),
            QtWidgets.QApplication.translate("MainWindow", "Page 1", None, -1),
        )
        self.label_110.setToolTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a tool tip", None, -1
            )
        )
        self.label_110.setStatusTip(
            QtWidgets.QApplication.translate(
                "MainWindow", "This is a status tip", None, -1
            )
        )
        self.label_110.setWhatsThis(
            QtWidgets.QApplication.translate(
                "MainWindow", 'This is "what is this"', None, -1
            )
        )
        self.label_110.setText(
            QtWidgets.QApplication.translate(
                "MainWindow", "Inside ToolBox Page 2", None, -1
            )
        )
        self.toolBoxDis_2.setItemText(
            self.toolBoxDis_2.indexOf(self.page_7),
            QtWidgets.QApplication.translate("MainWindow", "Page 2", None, -1),
        )
        self.menuMenu.setTitle(
            QtWidgets.QApplication.translate("MainWindow", "menu", None, -1)
        )
        self.actionAction.setText(
            QtWidgets.QApplication.translate("MainWindow", "action", None, -1)
        )
        self.actionCheckable_action.setText(
            QtWidgets.QApplication.translate("MainWindow", "checkable action", None, -1)
        )
