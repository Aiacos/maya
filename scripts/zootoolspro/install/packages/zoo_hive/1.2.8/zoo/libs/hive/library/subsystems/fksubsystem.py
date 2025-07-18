from zoo.libs.hive import api
from zoo.libs.maya import zapi
from zoo.libs.hive.base import basesubsystem


class FKSubsystem(basesubsystem.BaseSubsystem):
    """Generic FK Subsystem which only handles the creation of FK rig controls

    .. note:: Does not handle generation of guides.

    :param component:
    :type component: :class:`api.Component`
    :param guideIds: The guide ids for the controls to be built from.
    :type guideIds: list[str]
    :param fkIds: The fk ids that are used to both queries and set.
    :type fkIds: list[str]
    :param rootParentId: The parent node for the root Fk control.
    :type rootParentId: str
    :param nameIds: The name ids for the name resolving, if not specified then it will be the same as the fkIds
    :type nameIds: list[str]
    """
    def __init__(self, component, guideIds, fkIds, rootParentId, nameIds=None):
        super(FKSubsystem, self).__init__(component)
        self.guideIds = guideIds
        self.fkIds = fkIds
        self.rootParentId = rootParentId
        self.nameIds = nameIds or self.fkIds
        assert len(self.fkIds) == len(self.nameIds), "fkIds, and nameIds must be the same length"

    def setupRig(self, parentNode):
        if not self.active():
            return
        namer = self.component.namingConfiguration()
        comp = self.component
        rigLayer = comp.rigLayer()
        compName, compSide = self.component.name(), self.component.side()
        guides = comp.definition.guideLayer.findGuides(*self.guideIds)
        fkCtrlPt = rigLayer.taggedNode(self.rootParentId)

        for i, guide in enumerate(guides):
            fkGuideId = self.fkIds[i]

            fkControlName = namer.resolve(
                "controlName",
                {
                    "componentName": compName,
                    "side": compSide,
                    "system": api.constants.FKTYPE,
                    "id": self.nameIds[i],
                    "type": "control",
                },
            )
            fkCtrl = rigLayer.createControl(
                name=fkControlName,
                id=fkGuideId,
                translate=guide.translate,
                rotate=guide.rotate,
                parent=fkCtrlPt,
                rotateOrder=guide.rotateOrder,
                shape=guide.shape,
                shapeTransform=guide.shapeTransform,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                srts=[{"name": "_".join([fkControlName, "srt"])}],
            )

            fkCtrlPt = fkCtrl

    def matchTo(self, nodes):
        """Matches the current fk controls to the specified nodes in worldSpace.
        Returns the controls and the expected selectable.

        :param nodes:
        :type nodes: list[:class:`zapi.DagNode`]
        :return:
        :rtype: dict
        """
        rigLayer = self.component.rigLayer()

        controls = rigLayer.findControls(*self.fkIds)
        mats = [jnt.worldMatrix() for jnt in nodes]
        for ctrl, mat in zip(controls, mats):
            ctrl.setMatrix(mat * ctrl.parentInverseMatrix())

        return {"controls": controls, "selectables": [controls[-1]]}
