from zoo.libs.maya.mayacommand import command
from zoo.libs.maya.cmds.meta import metasplinerig


class AdditiveFKDeleteCommand(command.ZooCommandMaya):
    id = "zoo.maya.additiveFk.delete"
    creator = "Andrew Silke"
    isUndoable = True
    uiData = {"icon": "splineRig",
              "tooltip": "Deletes the additive FK",
              "label": "Delete Additive FK Rig",
              "color": "",
              "backgroundColor": ""
              }
    _modifier = None

    def doIt(self, meta=None, bake=False, message=True):
        """ Bake the controls

        :type meta: :class:`metaadditivefk.ZooMetaAdditiveFk`
        :return:
        :rtype: :class:`metaadditivefk.ZooMetaAdditiveFk`

        """

        meta.deleteSetup(bake=bake)
