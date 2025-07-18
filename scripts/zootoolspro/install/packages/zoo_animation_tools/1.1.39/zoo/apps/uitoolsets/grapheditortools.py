""" ---------- General Graph Editor Tools -------------
Randomize animation keyframe UI.

Author: Andrew Silke
"""
from functools import partial

from zoovendor.Qt import QtWidgets, QtCore

from zoo.libs import iconlib
from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs.maya.cmds.animation import generalanimation, animconstants, grapheditorfcurve, keyframes
from zoo.libs.maya.cmds.hotkeys import definedhotkeys

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

CYCLE_BUTTON_MODES = [("loopAbc", "Cycle Both Pre And Post"), ("loopAbc", "Cycle Pre Only"),
                      ("loopAbc", "Cycle Post Only")]
NUDGE_COMBO = ["Sel Objs", "Scene All"]


class GraphEditorTools(toolsetwidget.ToolsetWidget):
    id = "graphEditorTools"
    info = "Assorted animation Graph Editor tools."
    uiData = {"label": "Graph Editor Toolbox",
              "icon": "graphEditor",
              "tooltip": "Assorted animation Graph Editor tools.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-graph-editor-toolbox/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        pass

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget(), self.initAdvancedWidget()]

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self)
        return self.compactWidget

    def initAdvancedWidget(self):
        """Builds the Advanced GUI (self.advancedWidget) """
        self.advancedWidget = GuiAdvanced(parent=self, properties=self.properties, toolsetWidget=self)
        return self.advancedWidget

    def postContentSetup(self):
        """Last of the initialize code"""
        self.uiConnections()

    def defaultAction(self):
        """Double Click
        Double clicking the tools toolset icon will run this method
        Be sure "defaultActionDoubleClick": True is set inside self.uiData (meta data of this class)"""
        pass

    def currentWidget(self):
        """ Currently active widget

        :return:
        :rtype: GuiAdvanced or GuiCompact
        """
        return super(GraphEditorTools, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(GraphEditorTools, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    @toolsetwidget.ToolsetWidget.undoDecorator
    def snapKeysWholeFrames(self):
        generalanimation.snapKeysWholeFrames()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def snapKeysCurrent(self):
        generalanimation.snapKeysCurrent()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def eulerFilter(self):
        generalanimation.eulerFilter()

    def cycleModeMenuClicked(self):
        """Convenience as avoids undo decorator inner return func(*args, **kwargs) issue"""
        generalanimation.cycleAnimation(cycleMode=self.properties.cycleCombo.value,
                                        pre=True,
                                        post=True,
                                        displayInfinity=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def cycleAnimation(self, pre=True, post=True):
        """Cycles the animation either pre or post or both"""
        generalanimation.cycleAnimation(cycleMode=self.properties.cycleCombo.value,
                                        pre=pre,
                                        post=post,
                                        displayInfinity=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def removeCycleAnimation(self):
        generalanimation.removeCycleAnimation()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def toggleInfinity(self):
        generalanimation.toggleInfinity()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def hideInfinity(self):
        generalanimation.showInfinity(False)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def selObjGraph(self):
        generalanimation.selObjGraph()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def selGraphKeysTime(self):
        definedhotkeys.selectTimelineSelectionInGraph()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def timeToKey(self):
        generalanimation.timeToKey()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def insertKey(self):
        generalanimation.insertKey()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def animHold(self):
        generalanimation.animHold()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def animHoldReverse(self):
        generalanimation.animHold(reverse=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def bakeKeys(self):
        generalanimation.bakeKeys()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def copyKeys(self):
        generalanimation.copyKeys()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def pasteKeys(self):
        generalanimation.pasteKeys()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def graphEditorExpand(self):
        grapheditorfcurve.graphExpandConnections(expandConnections=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def graphEditorCollapse(self):
        grapheditorfcurve.graphExpandConnections(expandConnections=False)

    def offsetMultiplier(self):
        """For offset functions multiply shift and minimise if ctrl is held down
        If alt then call the reset option

        :return multiplier: multiply value, .2 if ctrl 5 if shift 1 if None
        :rtype multiplier: float
        :return reset: reset becomes true for resetting
        :rtype reset: bool
        """
        return 10.0, False

    @toolsetwidget.ToolsetWidget.undoDecorator
    def nudge(self, moveAfter=False, nudgeBackward=False, doubleClick=False, middleClick=False):
        multiplier = 1.0
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            multiplier = 5.0
        elif modifiers == QtCore.Qt.ControlModifier:
            multiplier = 2.0
        elif modifiers == QtCore.Qt.AltModifier:
            multiplier = 10.0

        if middleClick:
            multiplier *= 2.0

        offset = self.properties.nudgeAmountFloat.value
        if nudgeBackward:
            offset *= -1

        offset *= multiplier

        if self.properties.nudgeCombo.value == 0:
            operationMode = "selectedObjs"
        else:
            operationMode = "allObjs"

        keyframes.nudgeKeys(offset=offset,
                            operationMode=operationMode,
                            moveAfter=moveAfter)

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            # Cycle Menu ----------------------------
            widget.cycleAnimationBtn.clicked.connect(self.cycleAnimation)
            # Buttons -------------------------
            widget.toggleInfinityBtn.clicked.connect(self.toggleInfinity)
            widget.removeCycleAnimationBtn.clicked.connect(self.removeCycleAnimation)
            widget.snapKeysCurrentBtn.clicked.connect(self.snapKeysCurrent)
            widget.snapKeysWholeFramesBtn.clicked.connect(self.snapKeysWholeFrames)
            widget.eulerFilterBtn.clicked.connect(self.eulerFilter)
            widget.selObjGraphBtn.clicked.connect(self.selObjGraph)
            widget.selGraphKeysTimeBtn.clicked.connect(self.selGraphKeysTime)
            widget.timeToKeyBtn.clicked.connect(self.timeToKey)
            widget.insertKeyBtn.clicked.connect(self.insertKey)
            widget.bakeKeysBtn.clicked.connect(self.bakeKeys)
            widget.animHoldBtn.clicked.connect(self.animHold)
            widget.animHoldReverseBtn.clicked.connect(self.animHoldReverse)
            widget.copyKeysBtn.clicked.connect(self.copyKeys)
            widget.pasteKeysBtn.clicked.connect(self.pasteKeys)
            widget.expandBtn.clicked.connect(self.graphEditorExpand)
            widget.collapseBtn.clicked.connect(self.graphEditorCollapse)
            # Nudge -------------------------
            widget.nudgeBeforeBackwardBtn.clicked.connect(partial(self.nudge,
                                                                  moveAfter=False,
                                                                  nudgeBackward=True))
            widget.nudgeBeforeForwardBtn.clicked.connect(partial(self.nudge,
                                                                 moveAfter=False,
                                                                 nudgeBackward=False))
            widget.nudgeAfterBackwardBtn.clicked.connect(partial(self.nudge,
                                                                 moveAfter=True,
                                                                 nudgeBackward=True))
            widget.nudgeAfterForwardBtn.clicked.connect(partial(self.nudge,
                                                                moveAfter=True,
                                                                nudgeBackward=False))
            # double clicks -------------------------
            widget.nudgeBeforeBackwardBtn.leftDoubleClicked.connect(partial(self.nudge,
                                                                            moveAfter=False,
                                                                            nudgeBackward=True,
                                                                            doubleClick=True))
            widget.nudgeBeforeForwardBtn.leftDoubleClicked.connect(partial(self.nudge,
                                                                           moveAfter=False,
                                                                           nudgeBackward=False,
                                                                           doubleClick=True))
            widget.nudgeAfterBackwardBtn.leftDoubleClicked.connect(partial(self.nudge,
                                                                           moveAfter=True,
                                                                           nudgeBackward=True,
                                                                           doubleClick=True))
            widget.nudgeAfterForwardBtn.leftDoubleClicked.connect(partial(self.nudge,
                                                                          moveAfter=True,
                                                                          nudgeBackward=False,
                                                                          doubleClick=True))
            # middle clicks -------------------------
            widget.nudgeBeforeBackwardBtn.middleClicked.connect(partial(self.nudge,
                                                                        moveAfter=False,
                                                                        nudgeBackward=True,
                                                                        middleClick=True))
            widget.nudgeBeforeForwardBtn.middleClicked.connect(partial(self.nudge,
                                                                       moveAfter=False,
                                                                       nudgeBackward=False,
                                                                       middleClick=True))
            widget.nudgeAfterBackwardBtn.middleClicked.connect(partial(self.nudge,
                                                                       moveAfter=True,
                                                                       nudgeBackward=True,
                                                                       middleClick=True))
            widget.nudgeAfterForwardBtn.middleClicked.connect(partial(self.nudge,
                                                                      moveAfter=True,
                                                                      nudgeBackward=False,
                                                                      middleClick=True))
            # middle double clicks -------------------------
            widget.nudgeBeforeBackwardBtn.middleDoubleClicked.connect(partial(self.nudge,
                                                                              moveAfter=False,
                                                                              nudgeBackward=True,
                                                                              doubleClick=True,
                                                                              middleClick=True))
            widget.nudgeBeforeForwardBtn.middleDoubleClicked.connect(partial(self.nudge,
                                                                             moveAfter=False,
                                                                             nudgeBackward=False,
                                                                             doubleClick=True,
                                                                             middleClick=True))
            widget.nudgeAfterBackwardBtn.middleDoubleClicked.connect(partial(self.nudge,
                                                                             moveAfter=True,
                                                                             nudgeBackward=True,
                                                                             doubleClick=True,
                                                                             middleClick=True))
            widget.nudgeAfterForwardBtn.middleDoubleClicked.connect(partial(self.nudge,
                                                                            moveAfter=True,
                                                                            nudgeBackward=False,
                                                                            doubleClick=True,
                                                                            middleClick=True))

            # Right Click Save Menu ------------
            widget.cycleAnimationBtn.addAction("Loop Pre Infinity Only",
                                               mouseMenu=QtCore.Qt.RightButton,
                                               icon=iconlib.icon("loopAbc"),
                                               connect=partial(self.cycleAnimation, pre=True, post=False))
            widget.cycleAnimationBtn.addAction("Loop Post Infinity Only",
                                               mouseMenu=QtCore.Qt.RightButton,
                                               icon=iconlib.icon("loopAbc"),
                                               connect=partial(self.cycleAnimation, pre=False, post=True))
            widget.cycleAnimationBtn.addAction("Loop Pre/Post Infinity (default)",
                                               mouseMenu=QtCore.Qt.RightButton,
                                               icon=iconlib.icon("loopAbc"),
                                               connect=partial(self.cycleAnimation, pre=True, post=True))


class GuiWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None, properties=None, uiMode=None, toolsetWidget=None):
        """Builds the main widgets for all GUIs

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        :param uiMode: 0 is compact ui mode, 1 is advanced ui mode
        :type uiMode: int
        """
        super(GuiWidgets, self).__init__(parent=parent)
        self.properties = properties
        # Cycle Combo ---------------------------------------
        toolTip = "Cycles the selected objects for both pre and post. \n" \
                  "Right-Click to affect Pre or Post only. \n" \
                  "Zoo Hotkey: alt o (Regular Cycle)"
        self.cycleCombo = elements.ComboBoxRegular(label="",
                                                   labelRatio=16,
                                                   boxRatio=23,
                                                   items=animconstants.GRAPH_CYCLE_LONG,
                                                   parent=parent,
                                                   toolTip=toolTip)
        self.cycleAnimationBtn = elements.AlignedButton("Apply Cycle (right-click)",
                                                        icon="loopAbc",
                                                        toolTip=toolTip)
        # Toggle Infinity ---------------------------------
        toolTip = "Toggles the infinity display in the graph editor. \n" \
                  "Zoo Hotkey: shift i"
        self.toggleInfinityBtn = elements.AlignedButton("Toggle Infinity",
                                                        icon="infinite",
                                                        toolTip=toolTip)
        # Remove Cycle ---------------------------------
        toolTip = "Removes any cycling animation on the selected objects for both pre and post. \n" \
                  "Zoo Hotkey: ctrl alt o"
        self.removeCycleAnimationBtn = elements.AlignedButton("Remove Cycle",
                                                              icon="removeLoop",
                                                              toolTip=toolTip)
        # Snap Key Retain ----------------------------------
        toolTip = "Snaps the selected keys to whole frames. \n" \
                  "Zoo Hotkey: shift alt o"
        self.snapKeysWholeFramesBtn = elements.AlignedButton("Snap Whole Frames",
                                                             icon="magnet",
                                                             toolTip=toolTip)
        # Snap To Current Time ---------------------------------
        toolTip = "Snaps the selected graph keys to the current time. \n" \
                  "Zoo Hotkey: ctrl alt a"
        self.snapKeysCurrentBtn = elements.AlignedButton("Snap Keys To Current",
                                                         icon="snapTime",
                                                         toolTip=toolTip)
        # Time To Selected Key ---------------------------------
        toolTip = "Moves the time slider to the closest selected keyframe. \n" \
                  "Zoo Hotkey: shift alt a"
        self.timeToKeyBtn = elements.AlignedButton("Time To Selected Key",
                                                   icon="timeToSelected",
                                                   toolTip=toolTip)
        # Euler Filter Keyframes ----------------------------------
        toolTip = "Euler Filter for de-tangling gimbal aligned curve rotations. \n" \
                  "Zoo Hotkey: ctrl shift alt g"
        self.eulerFilterBtn = elements.AlignedButton("Euler Filter",
                                                     icon="rotateManipulator",
                                                     toolTip=toolTip)
        # Select Object From Graph Curve ---------------------------------
        toolTip = "Select an object from a graph curve selection. \n" \
                  "Zoo Hotkey: shift ctrl alt a"
        self.selObjGraphBtn = elements.AlignedButton("Sel Obj From FCurve",
                                                     icon="selectObject",
                                                     toolTip=toolTip)
        # Select Object From Graph Curve ---------------------------------
        toolTip = "From the object selection, select all graph keys at the current time or timeline selection. \n" \
                  "Zoo Hotkey: ctrl + shift + alt + x"
        self.selGraphKeysTimeBtn = elements.AlignedButton("Sel Graph Keys From Time",
                                                          icon="time",
                                                          toolTip=toolTip)

        # Insert Key Tool ----------------------------------
        toolTip = "Maya's Insert Key Tool.\n" \
                  "Inserts a keyframe at the current time without affecting graph curves.  \n" \
                  "Select animation curve/s, or will work on all keyed attributes. \n" \
                  "Zoo & Maya Hotkey 1: i (hold) middle click drag on curve \n" \
                  "Zoo & Maya Hotkey 2: alt i"
        self.insertKeyBtn = elements.AlignedButton("Insert Key Tool",
                                                   icon="insertKey",
                                                   toolTip=toolTip)
        # Bake ----------------------------------
        toolTip = "Bake animation for every frame on the selected objects. \n" \
                  "Works on the playback range \n" \
                  "Zoo Hotkey: shift alt b"
        self.bakeKeysBtn = elements.AlignedButton("Bake Playback Range",
                                                  icon="bake",
                                                  toolTip=toolTip)
        # Make Animation Hold ---------------------------------
        toolTip = "Make an animation hold. \n" \
                  "Place the timeline between two keys and run. \n" \
                  "The first key will be copied to the second with flat (auto) tangents. \n" \
                  "Zoo Hotkey: alt a"
        self.animHoldBtn = elements.AlignedButton("Make Anim Hold",
                                                  icon="animHold",
                                                  toolTip=toolTip)
        # Make Animation Hold ---------------------------------
        toolTip = "Make an animation hold (reversed). \n" \
                  "Place the timeline between two keys and run. \n" \
                  "The last key will be copied to the first with flat (auto) tangents. \n" \
                  "Zoo Hotkey: None"
        self.animHoldReverseBtn = elements.AlignedButton("Anim Hold (Reverse)",
                                                         icon="animHold",
                                                         toolTip=toolTip)
        # Copy Keyframes ----------------------------------
        toolTip = "Copy Keyframes in the Graph Editor. \n" \
                  "Zoo Hotkey: ctrl c"
        self.copyKeysBtn = elements.AlignedButton("Copy Keyframes",
                                                  icon="copy",
                                                  toolTip=toolTip)
        # Paste Keyframes ----------------------------------
        toolTip = "Paste Keyframes in the Graph Editor. \n" \
                  "Merge style paste mode. \n" \
                  "Zoo Hotkey: ctrl v"
        self.pasteKeysBtn = elements.AlignedButton("Paste Keyframes",
                                                   icon="paste",
                                                   toolTip=toolTip)
        # Graph Editor Expand ----------------------------------
        toolTip = "Graph Editor Expand Nodes \n" \
                  "Expands nodes in the Graph Editor sidebar (Maya default)."
        self.expandBtn = elements.AlignedButton("Graph Editor Expand",
                                                icon="arrowSingleDown",
                                                toolTip=toolTip)
        # Graph Editor Collapse ----------------------------------
        toolTip = "Graph Editor Collapse Nodes \n" \
                  "Collapses nodes in the Graph Editor sidebar. \n" \
                  "Solves `proxy attributes` that are displayed twice. \n" \
                  "Note: When the Graph Editor or Maya is closed this setting will be reset."
        self.collapseBtn = elements.AlignedButton("Graph Editor Collapse",
                                                  icon="arrowSingleUp",
                                                  toolTip=toolTip)
        # Nudge Amount ----------------------------------
        multiplierAmountTxt = "----- Multiplier Amount ----- \n" \
                              " Hold ctrl: x2 \n" \
                              " Hold shift: x5 \n" \
                              " Hold alt: x10 \n" \
                              " Double click: x2 \n" \
                              " Middle click: x2\n\n" \
                              "----- Hotkeys -----\n" \
                              "Nudge After x1: Shift Left Right Arrows\n" \
                              "Nudge After x5: Shift Left Right Arrows\n" \
                              "Nudge After x10: Shift Left Right Arrows\n" \
                              "Nudge Before x1: Shift Up Down Arrows\n" \
                              "Nudge Before x5: Shift Up Down Arrows\n" \
                              "Nudge Before x10: Shift Up Down Arrows "

        toolTip = "The amount to nudge the keys forward or backward. \n\n" \
                  "{}".format(multiplierAmountTxt)
        self.nudgeAmountFloat = elements.FloatEdit("Nudge By",
                                                   editText=1.0,
                                                   editRatio=1,
                                                   labelRatio=2,
                                                   toolTip=toolTip)
        # Nudge Combo ----------------------------------
        toolTip = "Nudge selected objects or the entire scene"
        self.nudgeCombo = elements.ComboBoxRegular(label="",
                                                   items=NUDGE_COMBO,
                                                   toolTip=toolTip)

        # Nudge Buttons ----------------------------------
        toolTip = ("Nudge Objects Backwards: \n\n"
                   "Priority for selected graph keys or the selected timeline. \n"
                   "If no keyframe selection will nudge the current time and earlier. \n\n "
                   "{}".format(multiplierAmountTxt))
        self.nudgeBeforeBackwardBtn = elements.styledButton(text="",
                                                            icon="nudgeBeforeBackward",
                                                            toolTip=toolTip,
                                                            parent=parent,
                                                            style=uic.BTN_TRANSPARENT_BG)
        toolTip = ("Nudge Objects Forwards: \n\n"
                   "Priority for selected graph keys or the selected timeline. \n"
                   "If no keyframe selection will nudge the current time and earlier. \n\n "
                   "{}".format(multiplierAmountTxt))
        self.nudgeBeforeForwardBtn = elements.styledButton(text="",
                                                           icon="nudgeBeforeForward",
                                                           toolTip=toolTip,
                                                           parent=parent,
                                                           style=uic.BTN_TRANSPARENT_BG)
        toolTip = ("Nudge Objects Backwards: \n\n"
                   "Priority for selected graph keys or the selected timeline. \n"
                   "If no keyframe selection will nudge the current time and after. \n\n "
                   "{}".format(multiplierAmountTxt))
        self.nudgeAfterBackwardBtn = elements.styledButton(text="",
                                                           icon="nudgeAfterBackward",
                                                           toolTip=toolTip,
                                                           parent=parent,
                                                           style=uic.BTN_TRANSPARENT_BG)
        toolTip = ("Nudge Objects Forwards: \n\n"
                   "Priority for selected graph keys or the selected timeline. \n"
                   "If no keyframe selection will nudge the current time and after. \n\n "
                   "{}".format(multiplierAmountTxt))
        self.nudgeAfterForwardBtn = elements.styledButton(text="",
                                                          icon="nudgeAfterForward",
                                                          toolTip=toolTip,
                                                          parent=parent,
                                                          style=uic.BTN_TRANSPARENT_BG)
        self.nudgeBeforeBackwardBtn.doubleClickEnabled = True
        self.nudgeBeforeForwardBtn.doubleClickEnabled = True
        self.nudgeAfterBackwardBtn.doubleClickEnabled = True
        self.nudgeAfterForwardBtn.doubleClickEnabled = True


class GuiCompact(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_COMPACT, toolsetWidget=None):
        """Adds the layout building the compact version of the GUI:

            default uiMode - 0 is advanced (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                         toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Nudge Options layout ---------------------------------------
        nudgeOptionsLayout = elements.hBoxLayout(spacing=uic.SVLRG)
        nudgeOptionsLayout.addWidget(self.nudgeAmountFloat, 2)
        nudgeOptionsLayout.addWidget(self.nudgeCombo, 1)
        # Nudge before layout ---------------------------------------
        nudgeLayout = elements.hBoxLayout(spacing=uic.SPACING)
        nudgeLayout.addWidget(self.nudgeBeforeBackwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeBeforeForwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeAfterBackwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeAfterForwardBtn, 1)

        # Cycle Combo Layout -----------------------------
        cycleComboLayout = elements.hBoxLayout()
        cycleComboLayout.addWidget(self.cycleCombo, 1)
        cycleComboLayout.addWidget(self.cycleAnimationBtn, 1)
        # Grid Layout ----------------------------------------------------------
        gridTopLayout = elements.GridLayout(spacing=uic.SPACING)
        row = 0
        gridTopLayout.addLayout(cycleComboLayout, row, 0, 1, 2)
        row += 1
        gridTopLayout.addWidget(self.toggleInfinityBtn, row, 0)
        gridTopLayout.addWidget(self.removeCycleAnimationBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.snapKeysCurrentBtn, row, 0)
        gridTopLayout.addWidget(self.snapKeysWholeFramesBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.eulerFilterBtn, row, 0)
        gridTopLayout.addWidget(self.bakeKeysBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.timeToKeyBtn, row, 0)
        gridTopLayout.addWidget(self.insertKeyBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.selObjGraphBtn, row, 0)
        gridTopLayout.addWidget(self.selGraphKeysTimeBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.animHoldBtn, row, 0)
        gridTopLayout.addWidget(self.animHoldReverseBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.expandBtn, row, 0)
        gridTopLayout.addWidget(self.collapseBtn, row, 1)
        row += 1
        gridTopLayout.addLayout(nudgeOptionsLayout, row, 0)
        gridTopLayout.addLayout(nudgeLayout, row, 1)
        gridTopLayout.setColumnStretch(0, 1)
        gridTopLayout.setColumnStretch(1, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(gridTopLayout)


class GuiAdvanced(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_ADVANCED, toolsetWidget=None):
        """Adds the layout building the advanced version of the GUI:

            default uiMode - 1 is advanced (UI_MODE_ADVANCED)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiAdvanced, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                          toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Nudge Options layout ---------------------------------------
        nudgeOptionsLayout = elements.hBoxLayout(spacing=uic.SVLRG)
        nudgeOptionsLayout.addWidget(self.nudgeAmountFloat, 2)
        nudgeOptionsLayout.addWidget(self.nudgeCombo, 1)
        # Nudge before layout ---------------------------------------
        nudgeLayout = elements.hBoxLayout(spacing=uic.SPACING)
        nudgeLayout.addWidget(self.nudgeBeforeBackwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeBeforeForwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeAfterBackwardBtn, 1)
        nudgeLayout.addWidget(self.nudgeAfterForwardBtn, 1)

        # Cycle Combo Layout -----------------------------
        cycleComboLayout = elements.hBoxLayout()
        cycleComboLayout.addWidget(self.cycleCombo, 1)
        cycleComboLayout.addWidget(self.cycleAnimationBtn, 1)
        # Grid Layout ----------------------------------------------------------
        gridTopLayout = elements.GridLayout(spacing=uic.SPACING)
        row = 0
        gridTopLayout.addLayout(cycleComboLayout, row, 0, 1, 2)
        row += 1
        gridTopLayout.addWidget(self.toggleInfinityBtn, row, 0)
        gridTopLayout.addWidget(self.removeCycleAnimationBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.snapKeysCurrentBtn, row, 0)
        gridTopLayout.addWidget(self.snapKeysWholeFramesBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.eulerFilterBtn, row, 0)
        gridTopLayout.addWidget(self.bakeKeysBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.timeToKeyBtn, row, 0)
        gridTopLayout.addWidget(self.insertKeyBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.selObjGraphBtn, row, 0)
        gridTopLayout.addWidget(self.selGraphKeysTimeBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.animHoldBtn, row, 0)
        gridTopLayout.addWidget(self.animHoldReverseBtn, row, 1)
        row += 1
        gridTopLayout.addWidget(self.expandBtn, row, 0)
        gridTopLayout.addWidget(self.collapseBtn, row, 1)
        row += 1
        gridTopLayout.addLayout(nudgeOptionsLayout, row, 0)
        gridTopLayout.addLayout(nudgeLayout, row, 1)
        row += 1
        gridTopLayout.addWidget(self.copyKeysBtn, row, 0)
        gridTopLayout.addWidget(self.pasteKeysBtn, row, 1)
        gridTopLayout.setColumnStretch(0, 1)
        gridTopLayout.setColumnStretch(1, 1)
        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(gridTopLayout)
