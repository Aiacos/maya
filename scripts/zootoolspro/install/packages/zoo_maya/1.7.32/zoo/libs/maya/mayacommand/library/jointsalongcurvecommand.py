from maya import cmds

from zoo.libs.maya.cmds.rig import jointsalongcurve
from zoo.libs.maya import zapi
from zoo.libs.maya.mayacommand import command


class JointsAlongCurveCommand(command.ZooCommandMaya):
    """Joints along curve that is undoable
    """
    id = "zoo.maya.jointsAlongCurve"
    creator = "Keen Foong"
    isUndoable = True
    useUndoChunk = False
    disableQueue = True

    uiData = {"icon": "",
              "tooltip": "",
              "label": "Distribute Joints Along Curve",
              "color": "",
              "backgroundColor": ""
              }
    _modifier = None
    _jointsList = None

    def resolveArguments(self, arguments):
        self._curve = zapi.nodeByName(arguments['splineCurve'])
        return arguments

    def doIt(self, **kwargs):
        """ Bake the controls

        :return:
        :rtype: list[:class:`DagNode`]

        """
        jointList = jointsalongcurve.jointsAlongACurve(**kwargs)
        self._jointsList = list(zapi.nodesByNames(jointList))
        return jointList

    def undoIt(self):
        """ Delete the joints if it exists

        :return:
        :rtype:
        """
        if self._jointsList:
            cmds.delete(zapi.fullNames(self._jointsList))
            self._curve.show()


class JointsAlongCurveSelectedCommand(command.ZooCommandMaya):
    """Joints along curve that is undoable
    """
    id = "zoo.maya.jointsAlongCurve.selected"
    creator = "Keen Foong"
    isUndoable = True
    useUndoChunk = False
    disableQueue = True

    uiData = {"icon": "",
              "tooltip": "",
              "label": "Distribute The Selected Joints Along Curve",
              "color": "",
              "backgroundColor": ""
              }
    _modifier = None
    _jointsList = None

    def doIt(self, **kwargs):
        """ Bake the controls

        :return:
        :rtype: list[:class:`DagNode`]

        """
        jointList = jointsalongcurve.jointsAlongACurveSelected(**kwargs)[0]
        self._jointsList = list(zapi.nodesByNames(jointList))
        return jointList

    def undoIt(self):
        """ Delete the joints if it exists

        :return:
        :rtype:
        """
        if self._jointsList:
            cmds.delete(zapi.fullNames(self._jointsList))


class JointsAlongCurveRebuildCommand(command.ZooCommandMaya):
    """Joints along curve that is undoable
    """
    id = "zoo.maya.jointsAlongCurve.rebuild"
    creator = "Keen Foong"
    isUndoable = True
    useUndoChunk = True
    disableQueue = False

    uiData = {"icon": "",
              "tooltip": "",
              "label": "Rebuild Joints along curve",
              "color": "",
              "backgroundColor": ""
              }
    _modifier = None
    _jointsList = None

    def doIt(self, **kwargs):
        """ Bake the controls

        :return:
        :rtype: list[:class:`DagNode`]

        """
        jointList = jointsalongcurve.rebuildSplineJointsSelected(**kwargs)
        # self._jointsList = list(zapi.nodesByNames(jointList))
        return jointList

    def undoIt(self):
        """ Delete the joints if it exists

        :return:
        :rtype:
        """
