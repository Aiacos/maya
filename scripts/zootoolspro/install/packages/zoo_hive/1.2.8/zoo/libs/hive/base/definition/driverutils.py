from zoo.libs.hive.base.definition import exprutils
from zoo.libs.hive.base import errors
from zoo.libs.maya import zapi


class DriverDirectParams(object):
    def __init__(self, driver, driven, driverAttribute, drivenAttribute):
        self.driver = driver
        self.driven = driven
        self.driverAttribute = driverAttribute
        self.drivenAttribute = drivenAttribute

    def serialize(self):
        return {"driver": self.driver,
                "driven": self.driven,
                "driverAttribute": self.driverAttribute,
                "drivenAttribute": self.drivenAttribute}


class DriverMatrixConstParams(object):
    def __init__(self, drivers, driven, maintainOffset=True):
        self.drivers = drivers
        self.driven = driven
        self.maintainOffset = maintainOffset

    def serialize(self):
        return {"drivers": self.drivers,
                "driven": self.driven,
                "maintainOffset": self.maintainOffset,
                }


class DriverDef(object):
    """Hive driver definition which defines a object driver eg. direct, sdk etc
    :param driverType: The driver definition type eg. direct, sdk etc
    :type driverType: str
    :param params: the params object
    :type params: :class:`DriverDirectParams` or :class:`DriverMatrixConstParams` or dict
    """

    def __init__(self, driverType, label, params):
        # driver type eg. "direct"
        self.type = driverType or ""
        self.label = label or ""
        # params for the driver type
        if isinstance(params, dict):
            if self.type == "direct":
                params = DriverDirectParams(**params)
            elif self.type == "matrixConstraint":
                params = DriverMatrixConstParams(**params)
        self.params = params or {}

    def serialize(self):
        return {
            "type": self.type,
            "label": self.label,
            "params": self.params.serialize() if self.params else {}
        }


def setupDriverDirect(rigInstance, component, logger, driverDef):
    driverExpr = driverDef.params.driver
    drivenExpr = driverDef.params.driven
    try:
        driverComp, driverNode = exprutils.attributeRefToSceneNode(rigInstance, component, driverExpr)
        if driverNode is None:
            raise errors.InvalidDefinitionAttrForSceneNode()
    except (errors.InvalidDefinitionAttrForSceneNode, errors.InvalidDefinitionAttrExpression):
        logger.warning("Unable to setup driver:{}, due to invalid "
                       "driver expression: {}".format(driverDef.label, driverExpr))
        return False
    try:
        drivenComp, drivenLayer = exprutils.attributeRefToLayerNode(rigInstance, component, drivenExpr)
        if drivenLayer is None:
            raise errors.InvalidDefinitionAttrForSceneNode()
    except (errors.InvalidDefinitionAttrForSceneNode, errors.InvalidDefinitionAttrExpression):
        logger.warning("Unable to setup driver:{}, due to invalid "
                       "driven expression: {}".format(driverDef.label, drivenExpr))
        return False
    driverAttr = driverNode.attribute(driverDef.params.driverAttribute)
    if not driverAttr:
        logger.warning("Unable to setup driver:{}, due to "
                       "invalid driver attribute: {}".format(driverDef.label, driverDef.params.driverAttribute))
        return False
    drivenAttr = drivenLayer.attribute(driverDef.params.drivenAttribute)
    if not drivenAttr:
        logger.warning("Unable to setup driver:{}, due to "
                       "invalid driven attribute: {}".format(driverDef.label, driverDef.params.drivenAttribute))
        return False

    driverAttr.connect(drivenAttr)
    return True


def setupDriverMatrixConstraint(rigInstance, component, logger, driverDef):
    """

    :param rigInstance:
    :type rigInstance:
    :param component:
    :type component:
    :param logger:
    :type logger:
    :param driverDef:
    :type driverDef: :class:`DriverDef`
    :return:
    :rtype:
    """
    params = driverDef.params  # type: DriverMatrixConstParams
    driversExpr = params.drivers
    drivenExpr = params.driven
    try:
        drivenComp, drivenNode = exprutils.attributeRefToSceneNode(
            rigInstance, component, drivenExpr
        )
        if drivenNode is None:
            raise errors.InvalidDefinitionAttrForSceneNode()
    except (
            errors.InvalidDefinitionAttrForSceneNode,
            errors.InvalidDefinitionAttrExpression,
    ):
        logger.warning(
            "Unable to setup driver:{}, due to invalid "
            "driven expression: {}".format(driverDef.label, drivenExpr)
        )
        return False
    drivers = {

        "targets": []
    }
    for driverLabel, driverExpr in driversExpr:
        try:
            driverComp, driverNode = exprutils.attributeRefToSceneNode(
                rigInstance, component, driverExpr
            )
            if driverNode is None:
                raise errors.InvalidDefinitionAttrForSceneNode()
            drivers["targets"].append((driverLabel, driverNode))
        except (errors.InvalidDefinitionAttrForSceneNode, errors.InvalidDefinitionAttrExpression):
            logger.warning("Unable to setup driver:{}, due to invalid "
                           "driver expression: {}".format(driverDef.label, driverExpr))
            continue
    if not drivers["targets"]:
        logger.warning("Unable to setup driver: {}, due to missing drivers".format(driverDef.label))
        return False
    #todo: add extras to component layer
    zapi.buildConstraint(
        drivenNode,
        drivers=drivers,
        constraintType="matrix",
        maintainOffset=driverDef.params.maintainOffset,
    )
    return True
