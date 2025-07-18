__all__ = [
    "TransformDefinition",
    "JointDefinition",
    "InputDefinition",
    "OutputDefinition",
    "ControlDefinition",
    "GuideDefinition",
]

import copy
from collections import OrderedDict

from zoo.libs.utils import general
from zoo.libs.maya import zapi
from zoo.libs.maya.utils import mayamath
from zoo.libs.maya.api import generic
from zoo.libs.hive.base.definition import definitionattrs
from zoo.libs.hive import constants


class DGNode(general.ObjectDict):
    @classmethod
    def deserialize(cls, data):
        """Given a Definition compatible dict recursively convert all children to Definitions
        and then return a new cls

        :param data: Same data as the class
        :type data: dict
        :rtype: :class:`TransformDefinition`
        """
        return cls(**data)

    def copy(self):
        return self.deserialize(self)

    def attribute(self, attributeName):
        for attr in self.get("attributes", []):
            if attr["name"] == attributeName:
                return attr


class TransformDefinition(general.ObjectDict):
    """
    :param kwargs: dict
    :type kwargs: dict

    Kwargs is in the form of

    .. code-block:: json

       {
           "name": "nodeName",
           "translation": [0,0,0],
           "rotation": [0,0,0,1],
           "rotateOrder": 0,
           "shape": "cube",
           "id": "myId",
           "children": [],
           "color": [0,0,0],
           "shapeTransform": {"translate": [0,0,0], "rotate": [0,0,0,1], "scale": [1,1,1]}
       }

    """

    DEFAULTS = {
        "name": "control",
        "children": list(),  # must exist but can be empty
        "parent": None,
        "hiveType": "transform",
        "type": "transform",
        "rotateOrder": 0,
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
    }

    def __init__(self, *args, **kwargs):
        defaults = copy.deepcopy(self.DEFAULTS)

        if args:
            defaults.update(args[0])

        defaults.update(kwargs)
        # ensure type compatibility
        for name in ("translate", "rotate", "scale"):
            existingData = defaults.get(name)
            if existingData is not None:
                defaults[name] = tuple(existingData)

        # todo: replace objectDict with standard dataclass so we remove old data
        for name in ("worldMatrix",):
            if defaults.get(name) is not None:
                del defaults[name]
        newAttrs = defaults.get("attributes", [])  # type: list[dict]
        attrInstances = []
        attrNames = set()
        # convert attributes to attribute def objects.
        for newAttr in newAttrs:
            if newAttr["name"] in attrNames:
                continue
            attrNames.add(newAttr["name"])
            attrInstances.append(definitionattrs.attributeClassForDef(newAttr))
        defaults["attributes"] = attrInstances
        super(TransformDefinition, self).__init__(defaults)
        if "translate" not in kwargs and "worldMatrix" in kwargs:
            self.worldMatrix = zapi.Matrix(kwargs["worldMatrix"])

    @property
    def translate(self):
        return zapi.Vector(self["translate"])

    @translate.setter
    def translate(self, value):
        self["translate"] = tuple(value)

    @property
    def rotate(self):
        rotation = self["rotate"]
        if len(rotation) == 3:
            return zapi.EulerRotation(
                rotation, self.get("rotateOrder", zapi.kRotateOrder_XYZ)
            )
        return zapi.Quaternion(rotation)

    @rotate.setter
    def rotate(self, value):
        self["rotate"] = tuple(value)

    @property
    def scale(self):
        return zapi.Vector(self["scale"])

    @scale.setter
    def scale(self, value):
        self["scale"] = tuple(value)

    @property
    def matrix(self):
        return zapi.Matrix(self["matrix"])

    @matrix.setter
    def matrix(self, value):
        self["matrix"] = tuple(value)

    @property
    def worldMatrix(self):
        transform = zapi.TransformationMatrix()
        transform.setTranslation(
            zapi.Vector(self.get("translate", (0, 0, 0))), zapi.kWorldSpace
        )
        rotation = self.get("rotate", (0, 0, 0, 1.0))
        if rotation:
            transform.setRotation(zapi.Quaternion(rotation))
        transform.setScale(self["scale"], zapi.kWorldSpace)
        return transform.asMatrix()

    @worldMatrix.setter
    def worldMatrix(self, value):
        transform = zapi.TransformationMatrix(zapi.Matrix(value))
        self["translate"] = tuple(transform.translation(zapi.kWorldSpace))
        self["rotate"] = tuple(transform.rotation(asQuaternion=True))
        self["scale"] = transform.scale(zapi.kWorldSpace)

    def attribute(self, attributeName):
        for attr in self.get("attributes", []):
            if attr["name"] == attributeName:
                return attr

    def iterChildren(self, recursive=True):
        """Generator function to recursively iterate through all children of this control

        :rtype: Generator(:class:`TransformDefinition`)
        """
        children = self.get("children", [])
        for child in iter(children):
            yield child
            if recursive:
                for subChild in child.iterChildren():
                    yield subChild

    @classmethod
    def deserialize(cls, data, parent=None):
        """Given a Definition compatible dict recursively convert all children to Definitions
        and then return a new cls

        :param data: Same data as the this class
        :type data: dict
        :param parent: The parent parent transform definition.
        :type parent: :class:`TransformDefinition`
        :rtype: :class:`TransformDefinition`
        """
        d = cls(**data)
        d.children = [
            cls.deserialize(child, parent=d.id) for child in d.get("children", [])
        ]
        d.parent = parent
        return d

    def copy(self):
        return self.deserialize(self, parent=self.parent)

    def deleteChild(self, childId):
        """Deletes a child definition from this transform.

        ..note: Only filters on the immediate transform children not recursively.
               If found then deletion will occur recursively. ie. all the childs children.

        :param childId: The child transform to delete
        :type childId: str
        :return: True if child was deleted.
        :rtype: bool
        """
        children = []
        deleted = False
        for child in self.iterChildren(recursive=False):
            if child.id != childId:
                children.append(child)
            else:
                deleted = True
        self["children"] = children
        return deleted

    def transformationMatrix(self, translate=True, rotate=True, scale=True):
        """Returns the world :class:`zapi.TransformationMatrix` instance for the current Definition.

        .. note::
            Requires the `translate`, `rotate`, `scale` keys on the definition. Rotate order key
            will be applied as well.


        :param translate: Include the translation part in the returned matrix
        :type translate: bool
        :param rotate: Include the rotation part in the returned matrix
        :type rotate: bool
        :param scale: Include the scale part in the returned matrix
        :type scale: bool
        :rtype: :class:`zapi.TransformationMatrix`
        """
        mat = zapi.TransformationMatrix()
        if translate:
            translation = self.get("translate")
            mat.setTranslation(
                zapi.Vector(translation or (0.0,0.0,0.0)), zapi.kWorldSpace
            )
        if rotate:
            rotation = self.get("rotate")
            mat.setRotation(zapi.Quaternion(rotation or (0.0, 0.0, 0.0, 1.0)))
            mat.reorderRotation(
                generic.intToMTransformRotationOrder(self.get("rotateOrder", 0))
            )
        if scale:
            scaleValue = self.get("scale")
            mat.setScale(scaleValue or (1.0, 1.0, 1.0), zapi.kWorldSpace)
        return mat


class JointDefinition(TransformDefinition):
    DEFAULTS = {
        "name": "joint",
        "id": "",
        "children": list(),  # must exist but can be empty
        "parent": None,
        "hiveType": "joint",
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
        "rotateOrder": 0,
    }


class InputDefinition(TransformDefinition):
    DEFAULTS = {
        "name": "input",
        "id": "",
        "root": False,  # determines if this Input Node is the connector for child-parent relationships
        "children": list(),  # must exist but can be empty
        "parent": None,
        "hiveType": "input",
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
        "rotateOrder": 0,
    }


class OutputDefinition(TransformDefinition):
    DEFAULTS = {
        "name": "output",
        "id": "",
        "root": False,
        "children": list(),  # must exist but can be empty
        "parent": None,
        "hiveType": "output",
        "rotateOrder": 0,
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
    }


class ControlDefinition(TransformDefinition):
    DEFAULTS = {
        "name": "control",
        "shape": "circle",
        "id": "ctrl",
        "color": (),
        "children": list(),  # must exist but can be empty
        "parent": None,
        "hiveType": "control",
        "srts": [],
        "rotateOrder": 0,
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
    }


class GuideDefinition(ControlDefinition):
    DEFAULTS = {
        # name is basically redundant now as we now dynamically rename guides
        "name": "GUIDE_RENAME",
        # nurbs curve/surface shape data
        "shape": {},
        # unique id for the guide
        "id": "GUIDE_RENAME",
        "children": [],
        "pivotColor": constants.DEFAULT_GUIDE_PIVOT_COLOR,
        "pivotShape": "sphere_arrow",
        "pivotShapeType": constants.GUIDE_TYPE_NURBS_CURVE,
        "parent": None,
        "hiveType": "guide",
        "translate": [0.0, 0.0, 0.0],
        "rotate": [0.0, 0.0, 0.0, 1.0],
        "scale": [1.0, 1.0, 1.0],
        "rotateOrder": 0,
        "internal": False,
        "mirror": True,
        "annotationParent": None,
        "shapeTransform": {
            "translate": [0.0, 0.0, 0.0],
            "scale": [1, 1, 1],
            "rotate": [0.0, 0.0, 0.0, 1.0],
            "rotateOrder": 0,
        },
        "srts": [],
        "attributes": [
            {
                "name": constants.AUTOALIGNAIMVECTOR_ATTR,
                "value": constants.DEFAULT_AIM_VECTOR,
                "Type": zapi.attrtypes.kMFnNumeric3Float,
                "default": constants.DEFAULT_AIM_VECTOR,
            },
            {
                "name": constants.AUTOALIGNUPVECTOR_ATTR,
                "value": constants.DEFAULT_UP_VECTOR,
                "Type": zapi.attrtypes.kMFnNumeric3Float,
                "default": constants.DEFAULT_UP_VECTOR
            }
        ]
    }

    def update(self, other=None, **kwargs):
        data = other or kwargs
        if not self.get("internal", False):
            self["parent"] = data.get("parent", self.get("parent"))
        self["shape"] = data.get("shape", self.get("shape"))
        self["shapeTransform"] = data.get("shapeTransform", self.get("shapeTransform"))
        self["rotateOrder"] = data.get("rotateOrder", self.get("rotateOrder"))
        self["pivotShapeType"] = data.get("pivotShapeType", self.get("pivotShapeType"))
        self["pivotShape"] = data.get("pivotShape", self.get("pivotShape"))
        if data.get("worldMatrix") and "translate" not in data:
            self.worldMatrix = data["worldMatrix"]
        else:
            self.translate = data.get("translate", self.get("translate"))
            self.rotate = data.get("rotate", self.get("rotate"))
            self.scale = data.get("scale", self.get("scale"))

        currentAttrs = self.get("attributes", [])
        currentAttrsMap = OrderedDict((i["name"], i) for i in currentAttrs)
        requestAttrs = OrderedDict((i["name"], i) for i in data.get("attributes", []))
        self.annotationParent = data.get(
            "annotationParent", self.get("annotationParent")
        )
        if currentAttrs:
            for mergeAttr in requestAttrs.values():
                existingAttr = currentAttrsMap.get(mergeAttr["name"])
                # todo: ignore any non defaults i think
                if existingAttr is None:
                    currentAttrs.append(definitionattrs.attributeClassForDef(mergeAttr))
                else:
                    existingAttr.update(mergeAttr)
        else:
            currentAttrs = [
                definitionattrs.attributeClassForDef(i) for i in requestAttrs.values()
            ]
        self["attributes"] = currentAttrs

    @property
    def annotationParent(self):
        return self.get("annotationParent") or self.parent

    @annotationParent.setter
    def annotationParent(self, value):
        self["annotationParent"] = value

    @property
    def shapeTransform(self):
        shapeTransformData = self["shapeTransform"]
        transform = zapi.TransformationMatrix()

        transform.setTranslation(
            zapi.Vector(shapeTransformData["translate"] or zapi.Vector()),
            zapi.kWorldSpace,
        )
        transform.setRotation(
            zapi.Quaternion(shapeTransformData["rotate"] or zapi.Quaternion())
        )
        transform.setScale(
            shapeTransformData["scale"] or (1.0, 1.0, 1.0), zapi.kWorldSpace
        )
        return transform.asMatrix()

    @shapeTransform.setter
    def shapeTransform(self, value):
        """ Setter for shapeTransform, takes a matrix in worldSpace.

        :param value: The worldSpace matrix for the shape.
        :type value: :class:`zapi.Matrix`
        """
        transform = zapi.TransformationMatrix(value)
        translate = transform.translation(zapi.kWorldSpace)
        self["shapeTransform"] = {
            "translate": tuple(translate),
            "rotate": tuple(transform.rotation(asQuaternion=True)),
            "scale": transform.scale(zapi.kWorldSpace),
        }

    @classmethod
    def deserialize(cls, data, parent=None):
        """Given a Definition compatible dict recursively convert all children to Definitions
        and then return a new cls

        :param data: Same data as this class data.
        :type data: dict
        :param parent: The parent guide definition.
        :type parent: :class:`GuideDefinition`
        :rtype: :class:`GuideDefinition`
        """
        d = super(GuideDefinition, cls).deserialize(data, parent=parent)
        d["srts"] = list(map(TransformDefinition, d.get("srts", [])))
        return d

    def addSrt(self, **srtInfo):
        self.srts.append(TransformDefinition(srtInfo))

    def aimVector(self):
        """Returns the aimVector value for the guide

        :rtype: :class:``zapi.Vector``
        """
        return self.attribute(constants.AUTOALIGNAIMVECTOR_ATTR).value

    def upVector(self):
        """Returns the upVector value for the guide

        :rtype: :class:``zapi.Vector``
        """
        return self.attribute(constants.AUTOALIGNUPVECTOR_ATTR).value

    def perpendicularVectorIndex(self):
        """Given the guides aim and up vector return which axis isn't being used and determine
        whether to get positive values from an incoming attribute whether it needs to be
        negated.

        :rtype: tuple[int, bool]
        """
        return mayamath.perpendicularAxisFromAlignVectors(self.aimVector(),
                                                          self.upVector())

    def mirrorScaleVector(self, invertUpVector=False, scale=(1.0, 1.0, 1.0), mirrorAxisIndex=None):
        """Returns the scale vector and whether the guide requires mirroring by scaling.
        Designed for the rig control creation so that a control is appropriately mirrored.
        Provide the result scale vector to the "scale" argument of `createControl`.

        :param invertUpVector:   Whether to invert the upVector of the scaled vector not just the plane vector.
        :type invertUpVector:  bool
        :param scale: The scale vector to mirror default is (1.0, 1.0, 1.0).
        :type scale: tuple[float] or :class:`zapi.Vector`
        :param mirrorAxisIndex: The axis to mirror instead using the guide settings.
        :type mirrorAxisIndex: int
        :return: The scale vector and whether the guide requires mirroring by scaling.
        :rtype: tuple[:class:`zapi.Vector`, bool]
        """
        upVector = self.attribute(constants.AUTOALIGNUPVECTOR_ATTR).value
        scaleOut = list(scale)
        if invertUpVector:
            scaleOut[mayamath.primaryAxisIndexFromVector(upVector)] *= -1.0

        isMirroredScaled = self.attribute(constants.MIRROR_SCALED_ATTR).value
        if isMirroredScaled:
            if mirrorAxisIndex is None:
                mirrorAxisIndex, _ = mayamath.perpendicularAxisFromAlignVectors(
                    self.attribute(constants.AUTOALIGNAIMVECTOR_ATTR).value,
                    upVector,
                )
            scaleOut[mirrorAxisIndex] *= -1.0
        return zapi.Vector(scaleOut), isMirroredScaled


HIVENODE_TYPES = {
    "transform": TransformDefinition,
    "guide": GuideDefinition,
    "control": ControlDefinition,
    "joint": JointDefinition,
    "input": InputDefinition,
    "output": OutputDefinition,
}
