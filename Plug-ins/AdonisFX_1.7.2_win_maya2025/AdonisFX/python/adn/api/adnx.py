import re
import logging
import math

import maya.cmds as cmds

import adn.tools.maya.locators as adn_locators
from adn.utils.maya.checkers import deformable_chain_exists
from adn.utils.maya.constants import MAYA_TO_ADN_RAMP_INTERP_MODE, ADN_TO_MAYA_RAMP_INTERP_MODE
from adn.commands.maya.scene import connect_attr



logging.warning("[AdonisFX]\nDISCLAIMER (adnx): This API is experimental, "
                "and will be subject to changes in following "
                "versions of AdonisFX.\nThe use of this API "
                "in production applications is not supported.")


class AdnTypes(object):
    kNone            =  0
    kMuscle          =  1  # Solver   AdnMuscle
    kSkin            =  2  # Solver   AdnSkin
    kFat             =  3  # Solver   AdnFat
    kGlue            =  4  # Solver   AdnGlue
    kSkinMerge       =  5  # Deformer AdnSkinMerge
    kRelax           =  6  # Deformer AdnRelax
    kSensorPosition  =  7  # Sensor   AdnSensorPosition
    kSensorDistance  =  8  # Sensor   AdnSensorDistance
    kSensorAngle     =  9  # Sensor   AdnSensorAngle
    kLocatorAdonis   = 10  # Locator  AdnLocator
    kLocatorPosition = 11  # Locator  AdnLocatorPosition
    kLocatorDistance = 12  # Locator  AdnLocatorDistance
    kLocatorAngle    = 13  # Locator  AdnLocatorAngle
    kActivation      = 14  # Util     AdnActivation
    kSimshape        = 15  # Solver   AdnSimshape
    kRibbon          = 16  # Solver   AdnRibbonMuscle
    kEdgeEvaluator   = 17  # Util     AdnEdgeEvaluator
    kRemap           = 18  # Util     AdnRemap
    kLast            = 18  # Last registered entity type


class AdnHost(object):
    kNone       =  0
    kMaya       =  1
    kHoudini    =  2
    kLast       =  2


class AdnRig(object):
    def __init__(self, host=AdnHost.kNone):
        self._host = host
        self._solvers = []
        self._deformers = []
        self._sensors = []
        self._utils = []

    def setHost(self, host):
        self._host = host

    def getHost(self):
        return self._host

    def addSolver(self, solver):
        logging.debug("Adding solver {0}".format(solver))
        self._solvers.append(solver)
        solver.setRig(self)

    def getSolvers(self):
        return self._solvers

    def addDeformer(self, deformer):
        logging.debug("Adding deformer {0}".format(deformer))
        self._deformers.append(deformer)
        deformer.setRig(self)

    def getDeformers(self):
        return self._deformers

    def addSensor(self, sensor):
        logging.debug("Adding sensor {0}".format(sensor))
        self._sensors.append(sensor)
        sensor.setRig(self)

    def getSensors(self):
        return self._sensors

    def addUtil(self, util):
        logging.debug("Adding utility {0}".format(util))
        self._utils.append(util)
        util.setRig(self)

    def getUtils(self):
        return self._utils

    def getData(self):
        data = {}
        if self._solvers:
            for solver in self._solvers:
                solver_data = solver.getData()
                solver_name = solver_data["name"]
                data[solver_name] = solver_data
        if self._sensors:
            for sensor in self._sensors:
                sensor_data = sensor.getData()
                sensor_name = sensor_data["name"]
                data[sensor_name] = sensor_data
        return data

    def fromDict(self, data):
        for entity_name in data.keys():
            entity_data = data[entity_name]
            entity_type = entity_data["type"]

            new_entity = None
            if entity_type == AdnTypes.kMuscle:
                new_entity = AdnMuscle(self)
            elif entity_type == AdnTypes.kSkin:
                new_entity = AdnSkin(self)
            elif entity_type == AdnTypes.kFat:
                new_entity = AdnFat(self)
            elif entity_type == AdnTypes.kGlue:
                new_entity = AdnGlue(self)                
            elif entity_type == AdnTypes.kSkinMerge:
                new_entity = AdnSkinMerge(self)                
            elif entity_type == AdnTypes.kRelax:
                new_entity = AdnRelax(self)                
            elif entity_type == AdnTypes.kSensorPosition:
                new_entity = AdnSensorPosition(self)                
            elif entity_type == AdnTypes.kSensorDistance:
                new_entity = AdnSensorDistance(self)                
            elif entity_type == AdnTypes.kSensorAngle:
                new_entity = AdnSensorRotation(self)                
            elif entity_type == AdnTypes.kLocatorAdonis:
                new_entity = AdnLocator(self)                
            elif entity_type == AdnTypes.kActivation:
                new_entity = AdnActivation(self)
            elif entity_type == AdnTypes.kSimshape:
                new_entity = AdnSimshape(self)
            elif entity_type == AdnTypes.kRibbon:
                new_entity = AdnRibbonMuscle(self)
            elif entity_type == AdnTypes.kEdgeEvaluator:
                new_entity = AdnEdgeEvaluator(self)
            elif entity_type == AdnTypes.kRemap:
                new_entity = AdnRemap(self)
                
            if new_entity:
                new_entity.fromDict(entity_data)

    def build(self):
        for solver in self._solvers:
            solver.build()
        for deformer in self._deformers:
            deformer.build()
        for sensor in self._sensors:
            sensor.build()
        for util in self._utils:
            util.build()

    def getConnections(self, node, ignore_at_destination=None, ignore_at_source=None):
        connections_list = []
        if self.getHost() == AdnHost.kMaya:
            all_connections = cmds.listConnections(node, plugs=True, connections=True) or []
            out_connections = cmds.listConnections(node, plugs=True, source=False, destination=True) or []
            for connection_index in range(int(len(all_connections)/2)):
                connection_a = all_connections[connection_index*2]
                connection_b = all_connections[connection_index*2+1]
                if connection_b in out_connections:
                    source = connection_a
                    destination = connection_b
                else:
                    source = connection_b
                    destination = connection_a
                if ignore_at_destination:
                    destination_node = destination.partition(".")[0]
                    if destination_node == node:
                        param = destination.partition(".")[-1]
                        param = param if "[" not in param else param.split("[")[0]
                        if param in ignore_at_destination:
                            continue
                if ignore_at_source:
                    source_node = source.partition(".")[0]
                    if source_node == node:
                        param = source.partition(".")[-1]
                        param = param if "[" not in param else param.split("[")[0]
                        if param in ignore_at_source:
                            continue
                connections_list.append((source, destination))
        return connections_list

    def setConnections(self, connections_list, node=None, ignore_at_destination=None, ignore_at_source=None):
        failed_connections = []
        for connection in connections_list:
            source, destination = connection
            if ignore_at_destination and node:
                destination_node = destination.partition(".")[0]
                if destination_node == node:
                    param = destination.partition(".")[-1]
                    param = param if "[" not in param else param.split("[")[0]
                    if param in ignore_at_destination:
                        continue
            if ignore_at_source and node:
                source_node = source.partition(".")[0]
                if source_node == node:
                    param = source.partition(".")[-1]
                    param = param if "[" not in param else param.split("[")[0]
                    if param in ignore_at_source:
                        continue

            # Skip the connections to the debugger as they will be
            # handled by the connect_to_debugger method
            destination_node = destination.partition(".")[0]
            if cmds.objExists(destination_node) and cmds.nodeType(destination_node) == "AdnDataNode":
                continue

            connection_made = connect_attr(connection[0], connection[1], force=True, log=False)
            if not connection_made:
                failed_connections.append(connection)
        return failed_connections


class AdnParameter(object):
    def __init__(self, name, value, value_type,
                 value_min=None, value_max=None):
        self.name = name
        self.value = value
        self.type = value_type
        self.min = value_min
        self.max = value_max

    def toDict(self):
        out_dictionary = dict()
        out_dictionary["name"] = self.name
        out_dictionary["type"] = self.type
        out_dictionary["value"] = self.value
        out_dictionary["min"] = self.min
        out_dictionary["max"] = self.max
        return out_dictionary

    def getData(self):
        return self.toDict()


class AdnConnection(object):
    def __init__(self, start_node=None, end_node=None, start_attribute=None, end_attribute=None):
        self.start_node = start_node
        self.end_node = end_node
        self.start_attribute = start_attribute
        self.end_attribute = end_attribute

    def toDict(self):
        out_dictionary = dict()
        out_dictionary["startNode"] = self.start_node
        out_dictionary["endNode"] = self.end_node
        out_dictionary["startAttribute"] = self.start_attribute
        out_dictionary["endAttribute"] = self.end_attribute
        return out_dictionary

    def getData(self):
        return self.toDict()


class AdnSolverBase(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "name": None,
            "type": AdnTypes.kNone,
            "geometry": None,
            "node": None,
            "enable": False,
            "iterations": 0,
            "stiffnessMultiplier": 1.0,
            "prerollStartTime": 0.0,
            "startTime": 0.0,
            "currentTime": 0.0,
            "timeScale": 1.0,
            "spaceScale": 1.0,
            "spaceScaleMode": -1,
            "gravity": 0.0,
            "gravityDirection": (0.0, -1.0, 0.0),
            "material": -1,
            "envelope": 0.0,
            "nodes": [],
            "connections": []
        }
        self._failed_connections = []
        if self not in rig.getSolvers():
            rig.addSolver(self)

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        available_parameters = ["name", "enable", "envelope", "iterations", "stiffnessMultiplier", 
            "prerollStartTime", "startTime", "currentTime", "timeScale", "spaceScale",
            "spaceScaleMode", "gravity", "gravityDirection", "geometry", "stiffness", "useCustomStiffness"]
        if parameter in available_parameters:
            self._data[parameter] = value
            return True

    def clear(self, force=False):
        if self._rig.getHost() == AdnHost.kMaya:
            for connection in self._connections:
                connection_start = "{0}.{1}".format(connection.start_node, connection.start_attribute)
                connection_end = "{0}.{1}".format(connection.end_node, connection.end_attribute)
                cmds.disconnectAttr(connection_start, connection_end)
            for node in self._nodes:
                cmds.delete(node)
            cmds.delete(self._node)

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self._failed_connections = []
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["enable", "envelope", "iterations", "stiffnessMultiplier", 
                "prerollStartTime", "startTime", "currentTime", "timeScale", 
                "spaceScale", "spaceScaleMode", "gravity", "gravityDirection",
                "geometry"]
            for parameter in parameters_list:
                value = None
                if cmds.attributeQuery(parameter, node=node, exists=True):
                    if parameter == "gravityDirection":
                        value = cmds.getAttr("{0}.{1}".format(node, parameter))[0]
                    else:
                        value = cmds.getAttr("{0}.{1}".format(node, parameter))
                elif parameter == "geometry" and "geometryFilter" in cmds.nodeType(node, inherited=True):
                    value = cmds.deformer(node, query=True, geometry=True)
                    if value is not None:
                        value = value[0]
                if value is not None:
                    self.setParameter(parameter, value)

    def update(self):
        self.preUpdate()

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True,
                                                     destination=False,
                                                     plugs=True,
                                                     connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                if destination.endswith("input[0].inputGeometry"):
                    continue
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}".format(source, destination))

    def getFailedConnections(self):
        return self._failed_connections


class AdnDeformerBase(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "name": None,
            "type": AdnTypes.kNone,
            "geometry": None,
            "node": None,
            "enable": False,
            "startTime": 0.0,
            "currentTime": 0.0,
            "envelope": 0,
            "weightMap": [],
            "nodes": [],
            "connections": []
        }
        self._failed_connections = []
        if self not in rig.getDeformers():
            rig.addDeformer(self)

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        available_parameters = ["name", "enable", "envelope", "iterations", "stiffnessMultiplier", 
            "prerollStartTime", "startTime", "currentTime", "timeScale", "spaceScale",
            "spaceScaleMode", "gravity", "gravityDirection", "geometry"]
        if parameter in available_parameters:
            self._data[parameter] = value
            return True

    def clear(self, force=False):
        if self._rig.getHost() == AdnHost.kMaya:
            for connection in self._connections:
                connection_start = "{0}.{1}".format(connection.start_node, connection.start_attribute)
                connection_end = "{0}.{1}".format(connection.end_node, connection.end_attribute)
                cmds.disconnectAttr(connection_start, connection_end)
            for node in self._nodes:
                cmds.delete(node)
            cmds.delete(self._node)

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self._failed_connections = []
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["enable", "envelope", "iterations", "stiffnessMultiplier", 
                "prerollStartTime", "startTime", "currentTime", "timeScale", 
                "spaceScale", "spaceScaleMode", "gravity", "gravityDirection",
                "geometry"]
            for parameter in parameters_list:
                value = None
                if cmds.attributeQuery(parameter, node=node, exists=True):
                    if parameter == "gravityDirection":
                        value = cmds.getAttr("{0}.{1}".format(node, parameter))[0]
                    else:
                        value = cmds.getAttr("{0}.{1}".format(node, parameter))
                elif parameter == "geometry" and "geometryFilter" in cmds.nodeType(node, inherited=True):
                    value = cmds.deformer(node, query=True, geometry=True)
                    if value is not None:
                        value = value[0]
                if value is not None:
                    self.setParameter(parameter, value)

        vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
        # Weight map
        weight_map = []
        for vertex_index in range(vertex_count):
            weight_map.append(cmds.getAttr("{0}.weightList[0].weights[{1}]".format(node, vertex_index)))
        self.setParameter("weightMap", weight_map)

    def update(self):
        self.preUpdate()
        node = self._data["node"]
        if self.getHost() == AdnHost.kMaya:
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            weights = self._data["weightMap"]
            if vertex_count != len(weights):
                logging.warning("{0}: mesh vertex count ({1}) does not match "
                                "the size of maps from data ({2})".format(node, vertex_count, len(weights)))
            max_vertex_count = min(vertex_count, len(weights))
            for vertex_index in range(max_vertex_count):
                cmds.setAttr("{0}.weightList[0].weights[{1}]".format(node, vertex_index), weights[vertex_index])

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True, destination=False, plugs=True, connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                if destination.endswith("input[0].inputGeometry"):
                    continue
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}".format(source, destination))

    def getFailedConnections(self):
        return self._failed_connections


class AdnFat(AdnSolverBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kFat
        # Solver Attributes
        self._data["substeps"] = 2
        self._data["material"] = 0
        self._data["stiffnessMultiplier"] = 1.0
        # Initialization Settings
        self._data["initHardAtStartTime"] = True
        self._data["initShapePreservationAtStartTime"] = True
        # Override Constraint Stiffness
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1000.0
        self._data["hardStiffnessOverride"] = -1.0
        self._data["volumeShapeStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        # Mass Properties
        self._data["pointMassMode"] = 0
        self._data["density"] = 900
        self._data["globalMassMultiplier"] = 1.0
        # Dynamic Properties
        self._data["globalDampingMultiplier"] = 0.1
        self._data["inertiaDamper"] = 0.0
        self._data["attenuationVelocityFactor"] = 1.0
        # Volume Structure
        self._data["divisions"] = 1
        # Maps
        self._data["globalDampingMap"] = []
        self._data["hardConstraintsMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["volumeShapePreservationMap"] = []
        # Input Attributes
        self._data["baseMatrix"] = None
        self._data["baseMesh"] = None
        self._data["attenuationMatrix"] = None
    
    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kFat
        # Solver Attributes
        self._data["substeps"] = 2
        self._data["material"] = 0
        self._data["stiffnessMultiplier"] = 1.0
        # Initialization Settings
        self._data["initHardAtStartTime"] = True
        self._data["initShapePreservationAtStartTime"] = True
        # Override Constraint Stiffness
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1000.0
        self._data["hardStiffnessOverride"] = -1.0
        self._data["volumeShapeStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        # Mass Properties
        self._data["pointMassMode"] = 0
        self._data["density"] = 900
        self._data["globalMassMultiplier"] = 1.0
        # Dynamic Properties
        self._data["globalDampingMultiplier"] = 0.1
        self._data["inertiaDamper"] = 0.0
        self._data["attenuationVelocityFactor"] = 1.0
        # Volume Structure
        self._data["divisions"] = 1
        # Maps
        self._data["globalDampingMap"] = []
        self._data["hardConstraintsMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["volumeShapePreservationMap"] = []
        # Input Attributes
        self._data["baseMatrix"] = None
        self._data["baseMesh"] = None
        self._data["attenuationMatrix"] = None
    
    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnFat")
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode("AdnFat", name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type="AdnFat",
                                         name=self._data["name"],
                                         frontOfChain=True)[0]

            adn_locators.connect_to_debugger(node)
            self.setParameter("node", node)
            self.update()
    
    def update(self):
        super().update()
        node = self._data["node"]
        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            for attribute in attributes_list:
                if attribute in ["type", "geometry", "node", "name", "nodes", "connections"]:
                    continue
                elif attribute == "gravityDirection":
                    cmds.setAttr("{0}.{1}".format(self.getName(), attribute),
                        self._data[attribute][0],
                        self._data[attribute][1],
                        self._data[attribute][2],
                        type="double3")
                elif attribute == "baseMesh":
                    base_mesh_name = self._data["baseMesh"]
                    if base_mesh_name:
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(base_matrix_name)
                        adn_base_mesh_attr = "{0}.baseMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_base_mesh_attr, force=True)
                elif attribute == "baseMatrix":
                    base_matrix_name = self._data["baseMatrix"]
                    if base_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(base_matrix_name)
                        adn_base_matrix_attr = "{0}.baseMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_base_matrix_attr, force=True)
                elif attribute == "attenuationMatrix":
                    attenuation_matrix_name = self._data["attenuationMatrix"]
                    if attenuation_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attenuation_matrix_name)
                        adn_attenuation_matrix_attr = "{0}.attenuationMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_attenuation_matrix_attr, force=True)
                elif attribute == "globalDampingMap":
                    weights = self._data["globalDampingMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "hardConstraintsMap":
                    weights = self._data["hardConstraintsMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.hardConstraintsList[0].hardConstraints[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "massMap":
                    weights = self._data["massMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.massList[0].mass[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "shapePreservationMap":
                    weights = self._data["shapePreservationMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "volumeShapePreservationMap":
                    weights = self._data["volumeShapePreservationMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.volumeShapePreservationList[0].volumeShapePreservation[{1}]".format(node, vertex_index), weights[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False)
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)
                        else:
                            logging.debug("Attribute {0} has an incoming connection. Cannot set value to {1}".format(attribute, value))
            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["substeps", "material", "stiffnessMultiplier", 
                               "initHardAtStartTime", "initShapePreservationAtStartTime",
                               "hardStiffnessOverride", "volumeShapeStiffnessOverride", "shapeStiffnessOverride",
                               "pointMassMode", "density", "globalMassMultiplier",
                               "globalDampingMultiplier", "inertiaDamper", "attenuationVelocityFactor",
                               "divisions", "stiffness", "useCustomStiffness"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            base_matrix = cmds.listConnections("{0}.baseMatrix".format(node)) or []
            base_matrix = base_matrix[0] if base_matrix else None
            self.setParameter("baseMatrix", base_matrix)
            base_mesh = cmds.listConnections("{0}.baseMesh".format(node)) or []
            base_mesh = base_mesh[0] if base_mesh else None
            self.setParameter("baseMesh", base_mesh)

            attenuation_matrix = cmds.listConnections("{0}.attenuationMatrix".format(node)) or []
            attenuation_matrix = attenuation_matrix[0] if attenuation_matrix else None
            self.setParameter("attenuationMatrix", attenuation_matrix)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Global Damping Map
            global_damping_map = []
            for i in range(vertex_count):
                global_damping_map.append(cmds.getAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, i)))
            self.setParameter("globalDampingMap", global_damping_map)
            # Hard Constraints Map
            hard_constraints_map = []
            for i in range(vertex_count):
                hard_constraints_map.append(cmds.getAttr("{0}.hardConstraintsList[0].hardConstraints[{1}]".format(node, i)))
            self.setParameter("hardConstraintsMap", hard_constraints_map)
            # Mass Map
            mass_map = []
            for i in range(vertex_count):
                mass_map.append(cmds.getAttr("{0}.massList[0].mass[{1}]".format(node, i)))
            self.setParameter("massMap", mass_map)
            # Hard Constraints Map
            shape_preservation_map = []
            for i in range(vertex_count):
                shape_preservation_map.append(cmds.getAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, i)))
            self.setParameter("shapePreservationMap", shape_preservation_map)
            # Soft Constraints Map
            volume_shape_preservation_map = []
            for i in range(vertex_count):
                volume_shape_preservation_map.append(cmds.getAttr("{0}.volumeShapePreservationList[0].volumeShapePreservation[{1}]".format(node, i)))
            self.setParameter("volumeShapePreservationMap", volume_shape_preservation_map)
            # Connections
            ignore_at_destination = ["baseMatrix", "baseMesh"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)
    
    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False


class AdnSkin(AdnSolverBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSkin
        self._data["material"] = 7
        self._data["targets"] = []
        self._data["compressionResistanceMap"] = []
        self._data["globalDampingMap"] = []
        self._data["hardConstraintsMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["slideConstraintsMap"] = []
        self._data["slidingDistanceMultiplierMap"] = []
        self._data["softConstraintsMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["stiffness"] = 1e5
        self._data["useCustomStiffness"] = False
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["distanceStiffnessOverride"] = -1.0
        self._data["hardStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideStiffnessOverride"] = -1.0
        self._data["softStiffnessOverride"] = -1.0
        self._data["pointMassMode"] = 1
        self._data["density"] = 1100
        self._data["globalMassMultiplier"] = 1.0
        self._data["triangulateMesh"] = False
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["maxSlidingDistance"] = 0.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["slidingConstraintsMode"] = 0
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initUberAtStartTime"] = True
        self._data["referenceMesh"] = None
        self._data["referenceMatrix"] = None
        self._data["attenuationMatrix"] = None
        self._data["substeps"] = 1
        self._data["selfCollisions"] = False
        self._data["scIterations"] = 1
        self._data["scPointRadiusScale"] = 1.0
        self._data["scPointRadiusMode"] = 1
        self._data["scSearchRadius"] = -1.0
        self._data["scPointRadiusMultiplierMap"] = []
        self._data["scWeightsMap"] = []

    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kSkin
        self._data["material"] = 7
        self._data["targets"] = []
        self._data["compressionResistanceMap"] = []
        self._data["globalDampingMap"] = []
        self._data["hardConstraintsMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["slideConstraintsMap"] = []
        self._data["slidingDistanceMultiplierMap"] = []
        self._data["softConstraintsMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["stiffness"] = 1e5
        self._data["useCustomStiffness"] = False
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["distanceStiffnessOverride"] = -1.0
        self._data["hardStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideStiffnessOverride"] = -1.0
        self._data["softStiffnessOverride"] = -1.0
        self._data["pointMassMode"] = 1
        self._data["density"] = 1100
        self._data["globalMassMultiplier"] = 1.0
        self._data["triangulateMesh"] = False
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["maxSlidingDistance"] = 0.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["slidingConstraintsMode"] = 0
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initUberAtStartTime"] = True
        self._data["referenceMesh"] = None
        self._data["referenceMatrix"] = None
        self._data["attenuationMatrix"] = None
        self._data["substeps"] = 1
        self._data["selfCollisions"] = False
        self._data["scIterations"] = 1
        self._data["scPointRadiusScale"] = 1.0
        self._data["scPointRadiusMode"] = 1
        self._data["scSearchRadius"] = -1.0
        self._data["scPointRadiusMultiplierMap"] = []
        self._data["scWeightsMap"] = []

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnSkin")
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode("AdnSkin", name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type="AdnSkin",
                                         name=self._data["name"],
                                         frontOfChain=True)[0]

            adn_locators.connect_to_debugger(node)
            self.setParameter("node", node)
            self.update()

    def update(self):
        super().update()
        node = self._data["node"]
        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            for attribute in attributes_list:
                if attribute in ["type", "geometry", "node", "name", "nodes", "connections"]:
                    continue
                elif attribute == "gravityDirection":
                    cmds.setAttr("{0}.{1}".format(self.getName(), attribute),
                        self._data[attribute][0],
                        self._data[attribute][1],
                        self._data[attribute][2],
                        type="double3")
                elif attribute == "attenuationMatrix":
                    attenuation_matrix_name = self._data["attenuationMatrix"]
                    if attenuation_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attenuation_matrix_name)
                        adn_attenuation_matrix_attr = "{0}.attenuationMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_attenuation_matrix_attr, force=True)
                elif attribute == "referenceMatrix":
                    reference_matrix_name = self._data["referenceMatrix"]
                    if reference_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(reference_matrix_name)
                        adn_reference_matrix_attr = "{0}.referenceMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_reference_matrix_attr, force=True)
                elif attribute == "referenceMesh":
                    reference_mesh_name = self._data["referenceMesh"]
                    if reference_mesh_name:
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(reference_mesh_name)
                        adn_reference_mesh_attr = "{0}.referenceMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_reference_mesh_attr, force=True)
                elif attribute == "targets":
                    targets_data = self._data["targets"]
                    for target_index in range(len(targets_data)):
                        target_name = targets_data[target_index]
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(target_name)
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(target_name)
                        adn_targets_attr = "{0}.targets".format(node)
                        adn_attachment_mesh = "{0}[{1}].targetWorldMesh".format(adn_targets_attr, target_index)
                        adn_attachment_matrix = "{0}[{1}].targetWorldMatrix".format(adn_targets_attr, target_index)
                        connect_attr(maya_attachment_mesh, adn_attachment_mesh, force=True)
                        connect_attr(maya_attachment_matrix, adn_attachment_matrix, force=True)
                elif attribute == "compressionResistanceMap":
                    weights = self._data["compressionResistanceMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "globalDampingMap":
                    weights = self._data["globalDampingMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "hardConstraintsMap":
                    weights = self._data["hardConstraintsMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.hardConstraintsList[0].hardConstraints[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "massMap":
                    weights = self._data["massMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.massList[0].mass[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "shapePreservationMap":
                    weights = self._data["shapePreservationMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "slideConstraintsMap":
                    weights = self._data["slideConstraintsMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.slideConstraintsList[0].slideConstraints[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "slidingDistanceMultiplierMap":
                    weights = self._data["slidingDistanceMultiplierMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "softConstraintsMap":
                    weights = self._data["softConstraintsMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.softConstraintsList[0].softConstraints[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "stretchingResistanceMap":
                    weights = self._data["stretchingResistanceMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "scPointRadiusMultiplierMap":
                    weights = self._data["scPointRadiusMultiplierMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.scPointRadiusMultiplierList[0].scPointRadiusMultiplier[{1}]".format(node, vertex_index), weights[vertex_index])
                elif attribute == "scWeightsMap":
                    weights = self._data["scWeightsMap"]
                    for vertex_index in range(len(weights)):
                        cmds.setAttr("{0}.scWeightsList[0].scWeights[{1}]".format(node, vertex_index), weights[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False)
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)
                        else:
                            logging.debug("Attribute {0} has an incoming connection. Cannot set value to {1}".format(attribute, value))

            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def addTarget(self, target):
        self._data["targets"].append(target)

    def getGeometryAttachment(self, index):
        return self._data["targets"][index]

    def findGeometryAttachment(self, attachment):
        if attachment in self._data["targets"]:
            index = self._data["targets"].index(attachment)
            return index

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["material", "distanceStiffnessOverride", "hardStiffnessOverride",
                               "shapeStiffnessOverride", "slideStiffnessOverride", "softStiffnessOverride",
                               "pointMassMode", "density", "globalMassMultiplier", "triangulateMesh",
                               "globalDampingMultiplier", "inertiaDamper", "restLengthMultiplier",
                               "maxSlidingDistance", "compressionMultiplier", "stretchingMultiplier",
                               "attenuationVelocityFactor", "slidingConstraintsMode",
                               "initShapePreservationAtStartTime", "initUberAtStartTime",
                               "useCustomStiffness", "stiffness", "overrideShapePreservationStiffness",
                               "stiffnessShapePreservation", "substeps", "selfCollisions", "scIterations",
                               "scPointRadiusScale", "scPointRadiusMode", "scSearchRadius"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            reference_mesh = cmds.listConnections("{0}.referenceMesh".format(node)) or []
            reference_mesh = reference_mesh[0] if reference_mesh else None
            self.setParameter("referenceMesh", reference_mesh)
            reference_matrix = cmds.listConnections("{0}.referenceMatrix".format(node)) or []
            reference_matrix = reference_matrix[0] if reference_matrix else None
            self.setParameter("referenceMatrix", reference_matrix)

            attenuation_matrix = cmds.listConnections("{0}.attenuationMatrix".format(node)) or []
            attenuation_matrix = attenuation_matrix[0] if attenuation_matrix else None
            self.setParameter("attenuationMatrix", attenuation_matrix)

            raw_targets = cmds.listConnections("{0}.targets".format(node)) or []
            unique_targets = set()
            targets = []
            for target in raw_targets:
                if target not in unique_targets:
                    unique_targets.add(target)
                    targets.append(target)
            self.setParameter("targets", targets)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Compression Resistance Map
            compression_resistance_map = []
            for i in range(vertex_count):
                compression_resistance_map.append(cmds.getAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, i)))
            self.setParameter("compressionResistanceMap", compression_resistance_map)
            # Stretching Resistance Map
            stretching_resistance_map = []
            for i in range(vertex_count):
                stretching_resistance_map.append(cmds.getAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, i)))
            self.setParameter("stretchingResistanceMap", stretching_resistance_map)
            # Global Damping Map
            global_damping_map = []
            for i in range(vertex_count):
                global_damping_map.append(cmds.getAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, i)))
            self.setParameter("globalDampingMap", global_damping_map)
            # Hard Constraints Map
            hard_constraints_map = []
            for i in range(vertex_count):
                hard_constraints_map.append(cmds.getAttr("{0}.hardConstraintsList[0].hardConstraints[{1}]".format(node, i)))
            self.setParameter("hardConstraintsMap", hard_constraints_map)
            # Soft Constraints Map
            soft_constraints_map = []
            for i in range(vertex_count):
                soft_constraints_map.append(cmds.getAttr("{0}.softConstraintsList[0].softConstraints[{1}]".format(node, i)))
            self.setParameter("softConstraintsMap", soft_constraints_map)
            # Sliding Constraints Map
            slide_constraints_map = []
            for i in range(vertex_count):
                slide_constraints_map.append(cmds.getAttr("{0}.slideConstraintsList[0].slideConstraints[{1}]".format(node, i)))
            self.setParameter("slideConstraintsMap", slide_constraints_map)
            # Max Sliding Distance Map
            sliding_distance_map = []
            for i in range(vertex_count):
                sliding_distance_map.append(cmds.getAttr("{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(node, i)))
            self.setParameter("slidingDistanceMultiplierMap", sliding_distance_map)
            # Masses Map
            masses_map = []
            for i in range(vertex_count):
                masses_map.append(cmds.getAttr("{0}.massList[0].mass[{1}]".format(node, i)))
            self.setParameter("massMap", masses_map)
            # Shape Preservation Map
            shape_preservation_map = []
            for i in range(vertex_count):
                shape_preservation_map.append(cmds.getAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, i)))
            self.setParameter("shapePreservationMap", shape_preservation_map)
            # Point Radius Multiplier Map
            point_radius_mult_map = []
            for i in range(vertex_count):
                point_radius_mult_map.append(cmds.getAttr("{0}.scPointRadiusMultiplierList[0].scPointRadiusMultiplier[{1}]".format(node, i)))
            self.setParameter("scPointRadiusMultiplierMap", point_radius_mult_map)
            # Self-Collisions Weights Map
            sc_weights_map = []
            for i in range(vertex_count):
                sc_weights_map.append(cmds.getAttr("{0}.scWeightsList[0].scWeights[{1}]".format(node, i)))
            self.setParameter("scWeightsMap", sc_weights_map)

            # Connections
            ignore_at_destination = ["targets"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)


class AdnMuscleBase(AdnSolverBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kNone
        self._data["material"] = 1
        self._data["activation"] = 0.0
        self._data["activationList"] = []
        self._data["restActivation"] = 0.0
        self._data["geometryAttachments"] = []
        self._data["transformAttachments"] = []
        self._data["segments"] = []
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1e5
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["attachmentToGeometryStiffnessOverride"] = -1.0
        self._data["attachmentToTransformStiffnessOverride"] = -1.0
        self._data["fiberStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideOnGeometryStiffnessOverride"] = -1.0
        self._data["slideOnSegmentStiffnessOverride"] = -1.0
        self._data["pointMassMode"] = 1
        self._data["density"] = 1060.0
        self._data["globalMassMultiplier"] = 1.0
        self._data["triangulateMesh"] = False
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["maxSlidingDistance"] = 0.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["hardAttachments"] = True
        self._data["slidingConstraintsMode"] = 0
        self._data["geometryAttachmentsMap"] = []
        self._data["transformAttachmentsMap"] = []
        self._data["slideOnSegmentMap"] = []
        self._data["compressionResistanceMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["geometrySlidingMap"] = []
        self._data["tendonsMap"] = []
        self._data["fibersDirectionMap"] = []
        self._data["fibersMultiplierMap"] = []
        self._data["maxSlidingDistanceMultiplierMap"] = []
        self._data["globalDampingMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["initFibersLengthsAtStartTime"] = True
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initExternalConstraintsAtStartTime"] = True
        self._data["attenuationMatrix"] = None
        self._data["debugFibersScale"] = 1.0

    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kNone
        self._data["material"] = 1
        self._data["activation"] = 0.0
        self._data["activationList"] = []
        self._data["restActivation"] = 0.0
        self._data["geometryAttachments"] = []
        self._data["transformAttachments"] = []
        self._data["segments"] = []
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1e5
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["attachmentToGeometryStiffnessOverride"] = -1.0
        self._data["attachmentToTransformStiffnessOverride"] = -1.0
        self._data["fiberStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideOnGeometryStiffnessOverride"] = -1.0
        self._data["slideOnSegmentStiffnessOverride"] = -1.0
        self._data["pointMassMode"] = 1
        self._data["density"] = 1060.0
        self._data["globalMassMultiplier"] = 1.0
        self._data["triangulateMesh"] = False
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["maxSlidingDistance"] = 0.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["hardAttachments"] = True
        self._data["slidingConstraintsMode"] = 0
        self._data["geometryAttachmentsMap"] = []
        self._data["transformAttachmentsMap"] = []
        self._data["slideOnSegmentMap"] = []
        self._data["compressionResistanceMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["geometrySlidingMap"] = []
        self._data["tendonsMap"] = []
        self._data["fibersDirectionMap"] = []
        self._data["fibersMultiplierMap"] = []
        self._data["maxSlidingDistanceMultiplierMap"] = []
        self._data["globalDampingMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["initFibersLengthsAtStartTime"] = True
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initExternalConstraintsAtStartTime"] = True
        self._data["attenuationMatrix"] = None
        self._data["debugFibersScale"] = 1.0

    def getTypeName(self):
        raise NotImplementedError("The AdnMuscleBase class does not implement getTypeName. " \
                                  "Please use the AdnMuscle or AdnRibbonMuscle subclasses.")

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type=self.getTypeName())
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode(self.getTypeName(), name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type=self.getTypeName(),
                                         name=self._data["name"],
                                         frontOfChain=True)[0]

            adn_locators.connect_to_debugger(node)
            self.setParameter("node", node)
            self.update()

    def update(self):
        super().update()
        node = self._data["node"]
        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            for attribute in attributes_list:
                if attribute in ["type", "geometry", "node", "name", "nodes", "connections", 
                    "geometryAttachmentsMap", "transformAttachmentsMap",
                    "geometrySlidingMap", "slideOnSegmentMap"]:
                    continue
                elif attribute == "gravityDirection":
                    cmds.setAttr("{0}.{1}".format(self.getName(), attribute),
                        self._data[attribute][0],
                        self._data[attribute][1],
                        self._data[attribute][2],
                        type="double3")
                elif attribute == "attenuationMatrix":
                    attenuation_matrix_name = self._data["attenuationMatrix"]
                    if attenuation_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attenuation_matrix_name)
                        adn_attenuation_matrix_attr = "{0}.attenuationMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_attenuation_matrix_attr, force=True)
                elif attribute == "activationList":
                    # Clear compound array attribute to avoid inconsistencies
                    attr_full_name = "{0}.{1}".format(node, attribute)
                    activation_list_indices = cmds.getAttr(attr_full_name, multiIndices=True) or []
                    for logical_index in activation_list_indices:
                        elem_full_name = "{0}[{1}]".format(attr_full_name, logical_index)
                        if cmds.objExists(elem_full_name):
                            cmds.removeMultiInstance(elem_full_name, b=True)
                    # Recreate the compound array attribute from data
                    if not self._data[attribute]:
                        continue
                    for elem in range(len(self._data[attribute])):
                        logical_index, bypass, operator, value = self._data[attribute][elem]
                        elem_full_name = "{0}.{1}[{2}]".format(node, attribute, logical_index)
                        # Set raw values only (connections are handled in `setConnections``)
                        cmds.setAttr("{0}.activationListBypassOperator".format(elem_full_name), bypass)
                        cmds.setAttr("{0}.activationListOperator".format(elem_full_name), operator)
                        cmds.setAttr("{0}.activationListValue".format(elem_full_name), value)
                elif attribute == "geometryAttachments":
                    attachments_data = self._data["geometryAttachments"]
                    for attachment_index in range(len(attachments_data)):
                        attachment_name = attachments_data[attachment_index]
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(attachment_name)
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attachment_name)
                        adn_targets_attr = "{0}.targets".format(node)
                        adn_attachment_mesh = "{0}[{1}].targetWorldMesh".format(adn_targets_attr, attachment_index)
                        adn_attachment_matrix = "{0}[{1}].targetWorldMatrix".format(adn_targets_attr, attachment_index)
                        connect_attr(maya_attachment_mesh, adn_attachment_mesh, force=True)
                        connect_attr(maya_attachment_matrix, adn_attachment_matrix, force=True)
                        geometryAttachmentsMap = self._data["geometryAttachmentsMap"]
                        if geometryAttachmentsMap and len(geometryAttachmentsMap) > attachment_index:
                            attachment_weights = geometryAttachmentsMap[attachment_index]
                            for vertex_index in range(len(attachment_weights)):
                                cmds.setAttr("{0}[{1}].attachmentToGeoConstraints[{2}]".format(adn_targets_attr, attachment_index, vertex_index), attachment_weights[vertex_index])
                        geometrySlidingMap = self._data["geometrySlidingMap"]
                        if geometrySlidingMap and len(geometrySlidingMap) > attachment_index:
                            sliding_weights = geometrySlidingMap[attachment_index]
                            for vertex_index in range(len(sliding_weights)):
                                cmds.setAttr("{0}[{1}].slideOnGeometryConstraints[{2}]".format(adn_targets_attr, attachment_index, vertex_index), sliding_weights[vertex_index])
                elif attribute == "transformAttachments":
                    attachments_data = self._data["transformAttachments"]
                    for attachment_index in range(len(attachments_data)):
                        attachment_name = attachments_data[attachment_index]
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attachment_name)
                        adn_targets_attr = "{0}.attachmentConstraintsList".format(node)
                        adn_attachment_matrix = "{0}[{1}].attachmentMatrix".format(adn_targets_attr, attachment_index)
                        connect_attr(maya_attachment_matrix, adn_attachment_matrix, force=True)
                        transformAttachmentsMap = self._data["transformAttachmentsMap"]
                        if transformAttachmentsMap and len(transformAttachmentsMap) > attachment_index:
                            attachment_weights = transformAttachmentsMap[attachment_index]
                            for vertex_index in range(len(attachment_weights)):
                                cmds.setAttr("{0}[{1}].attachmentConstraints[{2}]".format(adn_targets_attr, attachment_index, vertex_index), attachment_weights[vertex_index])
                elif attribute == "segments":
                    segments_data = self._data["segments"]
                    for segment_index in range(len(segments_data) // 2):
                        root_name = segments_data[segment_index * 2]
                        tip_name = segments_data[segment_index * 2 + 1]
                        maya_segment_root_matrix = "{0}.worldMatrix[0]".format(root_name)
                        maya_segment_tip_matrix = "{0}.worldMatrix[0]".format(tip_name)
                        adn_segments_attr = "{0}.slideOnSegmentConstraintsList".format(node)
                        adn_segment_root_matrix = "{0}[{1}].slideOnSegmentRootMatrix".format(adn_segments_attr, segment_index)
                        adn_segment_tip_matrix = "{0}[{1}].slideOnSegmentTipMatrix".format(adn_segments_attr, segment_index)
                        connect_attr(maya_segment_root_matrix, adn_segment_root_matrix, force=True)
                        connect_attr(maya_segment_tip_matrix, adn_segment_tip_matrix, force=True)
                        slideOnSegmentMap = self._data["slideOnSegmentMap"][segment_index]
                        for vertex_index in range(len(slideOnSegmentMap)):
                            cmds.setAttr("{0}[{1}].slideOnSegmentConstraints[{2}]".format(adn_segments_attr, segment_index, vertex_index), slideOnSegmentMap[vertex_index])
                elif attribute == "tendonsMap":
                    tendons_weights = self._data["tendonsMap"]
                    for vertex_index in range(len(tendons_weights)):
                        cmds.setAttr("{0}.tendonsList[0].tendons[{1}]".format(node, vertex_index), tendons_weights[vertex_index])
                elif attribute == "shapePreservationMap":
                    shape_preservation_weights = self._data["shapePreservationMap"]
                    for vertex_index in range(len(shape_preservation_weights)):
                        cmds.setAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, vertex_index), shape_preservation_weights[vertex_index])
                elif attribute == "fibersMultiplierMap":
                    fibers_multiplier_weights = self._data["fibersMultiplierMap"]
                    for vertex_index in range(len(fibers_multiplier_weights)):
                        cmds.setAttr("{0}.fibersMultiplierList[0].fibersMultiplier[{1}]".format(node, vertex_index), fibers_multiplier_weights[vertex_index])
                elif attribute == "fibersDirectionMap":
                    fibers_direction_map = self._data["fibersDirectionMap"]
                    for vertex_index in range(len(fibers_direction_map)):
                        cmds.setAttr("{0}.fibersList[0].fibers[{1}].fibersX".format(node, vertex_index), fibers_direction_map[vertex_index][0])
                        cmds.setAttr("{0}.fibersList[0].fibers[{1}].fibersY".format(node, vertex_index), fibers_direction_map[vertex_index][1])
                        cmds.setAttr("{0}.fibersList[0].fibers[{1}].fibersZ".format(node, vertex_index), fibers_direction_map[vertex_index][2])
                elif attribute == "compressionResistanceMap":
                    compression_resistance_map = self._data["compressionResistanceMap"]
                    for vertex_index in range(len(compression_resistance_map)):
                        cmds.setAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, vertex_index), compression_resistance_map[vertex_index])
                elif attribute == "stretchingResistanceMap":
                    stretching_resistance_map = self._data["stretchingResistanceMap"]
                    for vertex_index in range(len(stretching_resistance_map)):
                        cmds.setAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, vertex_index), stretching_resistance_map[vertex_index])
                elif attribute == "maxSlidingDistanceMultiplierMap":
                    max_sliding_distance_map = self._data["maxSlidingDistanceMultiplierMap"]
                    for vertex_index in range(len(max_sliding_distance_map)):
                        cmds.setAttr("{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(node, vertex_index), max_sliding_distance_map[vertex_index])
                elif attribute == "globalDampingMap":
                    global_damping_map = self._data["globalDampingMap"]
                    for vertex_index in range(len(global_damping_map)):
                        cmds.setAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, vertex_index), global_damping_map[vertex_index])
                elif attribute == "massMap":
                    mass_map = self._data["massMap"]
                    for vertex_index in range(len(mass_map)):
                        cmds.setAttr("{0}.massList[0].mass[{1}]".format(node, vertex_index), mass_map[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False)
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)
                        else:
                            logging.debug("Attribute {0} has an incoming connection. Cannot set value to {1}".format(attribute, value))

            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)

    def addGeometryAttachment(self, attachment):
        self._data["geometryAttachments"].append(attachment)
        self._data["geometryAttachmentsMap"].append([])

    def getGeometryAttachment(self, index):
        return self._data["geometryAttachments"][index]

    def findGeometryAttachment(self, attachment):
        if attachment in self._data["geometryAttachments"]:
            index = self._data["geometryAttachments"].index(attachment)
            return index

    def setGeometryAttachmentMap(self, index, values_map):
        self._data["geometryAttachmentsMap"][index] = values_map

    def addTransformAttachment(self, attachment):
        self._data["transformAttachments"].append(attachment)
        self._data["transformAttachmentsMap"].append([])

    def getTransformAttachment(self, index):
        return self._data["transformAttachments"][index]

    def findTransformAttachment(self, attachment):
        if attachment in self._data["transformAttachments"]:
            index = self._data["transformAttachments"].index(attachment)
            return index

    def setTransformAttachmentMap(self, index, values_map):
        self._data["transformAttachmentsMap"][index] = values_map

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["material", "activation", "restActivation",
                "attachmentToGeometryStiffnessOverride", "attachmentToTransformStiffnessOverride",
                "fiberStiffnessOverride", "shapeStiffnessOverride", "slideOnGeometryStiffnessOverride",
                "slideOnSegmentStiffnessOverride", "pointMassMode", "density", "globalMassMultiplier",
                "triangulateMesh", "globalDampingMultiplier", "inertiaDamper", "restLengthMultiplier",
                "maxSlidingDistance", "compressionMultiplier", "stretchingMultiplier",
                "attenuationVelocityFactor", "hardAttachments", "slidingConstraintsMode",
                "initFibersLengthsAtStartTime", "initShapePreservationAtStartTime",
                "initExternalConstraintsAtStartTime", "useCustomStiffness", "stiffness",
                "overrideShapePreservationStiffness", "stiffnessShapePreservation",
                "debugFibersScale"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            attenuation_matrix = cmds.listConnections("{0}.attenuationMatrix".format(node)) or []
            attenuation_matrix = attenuation_matrix[0] if attenuation_matrix else None
            self.setParameter("attenuationMatrix", attenuation_matrix)

            # Retrieve activation list
            activation_list = []
            activation_list_indices = cmds.getAttr("{0}.activationList".format(node), multiIndices=True) or []
            for logical_index in activation_list_indices:
                child_plug_name = "{0}.activationList[{1}]".format(node, logical_index)
                # Raw values
                bypass = cmds.getAttr("{0}.activationListBypassOperator".format(child_plug_name))
                operator = cmds.getAttr("{0}.activationListOperator".format(child_plug_name))
                value = cmds.getAttr("{0}.activationListValue".format(child_plug_name))
                # Tuple with 4 entries: logical index (required to support in/out sparse connections), bypass, operator, value
                activation_list.append((logical_index, bypass, operator, value))
            self.setParameter("activationList", activation_list)

            # Retrieve targets
            logical_indices = cmds.getAttr("{0}.targets".format(node), multiIndices=True) or []
            connected_target_indices = []
            geometry_attachments = []
            for idx in logical_indices:
                target_matrix = cmds.listConnections("{0}.targets[{1}].targetWorldMatrix".format(node, idx)) or []
                target_mesh = cmds.listConnections("{0}.targets[{1}].targetWorldMesh".format(node, idx)) or []
                # Check if both plugs are connected
                if target_matrix and target_mesh:
                    geometry_attachments.append(target_mesh[0])
                    connected_target_indices.append(idx)
            self.setParameter("geometryAttachments", geometry_attachments)

            # Retrieve segments
            logical_indices = cmds.getAttr("{0}.slideOnSegmentConstraintsList".format(node), multiIndices=True) or []
            connected_segment_indices = []
            segments = []
            for idx in logical_indices:
                root_matrix = cmds.listConnections("{0}.slideOnSegmentConstraintsList[{1}].slideOnSegmentRootMatrix".format(node, idx)) or []
                tip_matrix = cmds.listConnections("{0}.slideOnSegmentConstraintsList[{1}].slideOnSegmentTipMatrix".format(node, idx)) or []
                # Check if both plugs are connected
                if root_matrix and tip_matrix:
                    segments.append(root_matrix[0])
                    segments.append(tip_matrix[0])
                    connected_segment_indices.append(idx)
            self.setParameter("segments", segments)

            # Retrieve attachments to transform
            logical_indices = cmds.getAttr("{0}.attachmentConstraintsList".format(node), multiIndices=True) or []
            connected_transform_indices = []
            transform_attachments = []
            for idx in logical_indices:
                attachment_matrix = cmds.listConnections("{0}.attachmentConstraintsList[{1}].attachmentMatrix".format(node, idx)) or []
                # Check if the plug is connected
                if attachment_matrix:
                    transform_attachments.append(attachment_matrix[0])
                    connected_transform_indices.append(idx)
            self.setParameter("transformAttachments", transform_attachments)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Attachments to Geometry Map
            geometry_attachments_map = []
            for attachment_index in connected_target_indices:
                attachments_map = []
                for i in range(vertex_count):
                    attachments_map.append(cmds.getAttr("{0}.targets[{1}].attachmentToGeoConstraints[{2}]".format(node, attachment_index, i)))
                geometry_attachments_map.append(attachments_map)
            self.setParameter("geometryAttachmentsMap", geometry_attachments_map)
            # Slide on Geometry Map
            sliding_attachments_map = []
            for attachment_index in connected_target_indices:
                sliding_map = []
                for i in range(vertex_count):
                    sliding_map.append(cmds.getAttr("{0}.targets[{1}].slideOnGeometryConstraints[{2}]".format(node, attachment_index, i)))
                sliding_attachments_map.append(sliding_map)
            self.setParameter("geometrySlidingMap", sliding_attachments_map)
            # Attachments to Transform Map
            transform_attachments_map = []
            for attachment_index in connected_transform_indices:
                attachments_map = []
                for i in range(vertex_count):
                    attachments_map.append(cmds.getAttr("{0}.attachmentConstraintsList[{1}].attachmentConstraints[{2}]".format(node, attachment_index, i)))
                transform_attachments_map.append(attachments_map)
            self.setParameter("transformAttachmentsMap", transform_attachments_map)
            # Slide on Segment Map
            slide_on_segments_map = []
            for segment_index in connected_segment_indices:
                sliding = []
                for i in range(vertex_count):
                    sliding.append(cmds.getAttr("{0}.slideOnSegmentConstraintsList[{1}].slideOnSegmentConstraints[{2}]".format(node, segment_index, i)))
                slide_on_segments_map.append(sliding)
            self.setParameter("slideOnSegmentMap", slide_on_segments_map)
            # Shape Preservation Map
            shape_preservation_map = []
            for i in range(vertex_count):
                shape_preservation_map.append(cmds.getAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, i)))
            self.setParameter("shapePreservationMap", shape_preservation_map)
            # Tendons Map
            tendons_map = []
            for i in range(vertex_count):
                tendons_map.append(cmds.getAttr("{0}.tendonsList[0].tendons[{1}]".format(node, i)))
            self.setParameter("tendonsMap", tendons_map)
            # Compression Resistance Map
            compression_resistance_map = []
            for i in range(vertex_count):
                compression_resistance_map.append(cmds.getAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, i)))
            self.setParameter("compressionResistanceMap", compression_resistance_map)
            # Stretching Resistance Map
            stretching_resistance_map = []
            for i in range(vertex_count):
                stretching_resistance_map.append(cmds.getAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, i)))
            self.setParameter("stretchingResistanceMap", stretching_resistance_map)
            # Fibers Multiplier Map
            fibers_multiplier_map = []
            for i in range(vertex_count):
                fibers_multiplier_map.append(cmds.getAttr("{0}.fibersMultiplierList[0].fibersMultiplier[{1}]".format(node, i)))
            self.setParameter("fibersMultiplierMap", fibers_multiplier_map)
            # Fibers Direction Map
            fibers_direction_map = []
            for i in range(vertex_count):
                fibers_direction_map.append([
                    cmds.getAttr("{0}.fibersList[0].fibers[{1}].fibersX".format(node, i)),
                    cmds.getAttr("{0}.fibersList[0].fibers[{1}].fibersY".format(node, i)),
                    cmds.getAttr("{0}.fibersList[0].fibers[{1}].fibersZ".format(node, i))])
            self.setParameter("fibersDirectionMap", fibers_direction_map)
            # Max Sliding Distance Multiplier Map
            max_sliding_distance_map = []
            for i in range(vertex_count):
                max_sliding_distance_map.append(
                    cmds.getAttr("{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(node, i)))
            self.setParameter("maxSlidingDistanceMultiplierMap", max_sliding_distance_map)
            # Global Damping Map
            global_damping_map = []
            for i in range(vertex_count):
                global_damping_map.append(cmds.getAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, i)))
            self.setParameter("globalDampingMap", global_damping_map)
            # Mass Map
            mass_map = []
            for i in range(vertex_count):
                mass_map.append(cmds.getAttr("{0}.massList[0].mass[{1}]".format(node, i)))
            self.setParameter("massMap", mass_map)

            # Connections
            ignore_at_destination = ["targets", "attachmentConstraintsList", "slideOnSegmentConstraintsList"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)


class AdnMuscle(AdnMuscleBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kMuscle
        self._data["volumePreservation"] = 1.0
        self._data["volumeRatio"] = 1.0
        self._data["volumeActivationRatio"] = 1.0
        self._data["volumeStiffnessOverride"] = -1.0

    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kMuscle
        self._data["volumePreservation"] = 1.0
        self._data["volumeRatio"] = 1.0
        self._data["volumeActivationRatio"] = 1.0
        self._data["volumeStiffnessOverride"] = -1.0

    def getTypeName(self):
        return "AdnMuscle"

    def fromNode(self, node):
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["volumePreservation", "volumeRatio",
                               "volumeStiffnessOverride", "volumeActivationRatio"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)


class AdnRibbonMuscle(AdnMuscleBase):
    def  __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kRibbon

    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kRibbon

    def getTypeName(self):
        return "AdnRibbonMuscle"


class AdnSimshape(AdnSolverBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSimshape
        self._data["material"] = 7
        self._data["triangulateMesh"] = False
        self._data["pointMassMode"] = 1
        self._data["density"] = 1100.0
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1e5
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["distanceStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideCollisionStiffnessOverride"] = -1.0
        self._data["globalMassMultiplier"] = 1.0
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["attractionMultiplier"] = 1.0
        self._data["attractionRemapMode"] = 3
        self._data["musclesFile"] = ""
        self._data["activationSmoothing"] = 1
        self._data["animatableRestMesh"] = False
        self._data["activationMode"] = 2
        self._data["maxCollisionSlidingDistance"] = 0.0
        self._data["keepCollisionOrientation"] = True
        self._data["computeCollisions"] = True
        self._data["bidirectionalActivation"] = False
        self._data["writeOutActivation"] = False
        self._data["initializeToAnimMesh"] = False
        self._data["attenuationMatrix"] = None
        self._data["collisionMeshMatrix"] = None
        self._data["collisionRestMeshMatrix"] = None
        self._data["deformMesh"] = None
        self._data["animMesh"] = None
        self._data["restMesh"] = None
        self._data["collisionMesh"] = None
        self._data["collisionRestMesh"] = None
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initSlideCollisionAtStartTime"] = True
        self._data["attractForceMap"] = []
        self._data["collisionThresholdMultiplierMap"] = []
        self._data["compressionResistanceMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["globalDampingMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["slideCollisionConstraintsMap"] = []

    def reset(self):
        super().reset()
        self._data["type"] = AdnTypes.kSimshape
        self._data["material"] = 7
        self._data["triangulateMesh"] = False
        self._data["pointMassMode"] = 1
        self._data["density"] = 1100.0
        self._data["useCustomStiffness"] = False
        self._data["stiffness"] = 1e5
        self._data["overrideShapePreservationStiffness"] = False
        self._data["stiffnessShapePreservation"] = 1000.0
        self._data["distanceStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["slideCollisionStiffnessOverride"] = -1.0
        self._data["globalMassMultiplier"] = 1.0
        self._data["globalDampingMultiplier"] = 0.75
        self._data["inertiaDamper"] = 0.0
        self._data["restLengthMultiplier"] = 1.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["attractionMultiplier"] = 1.0
        self._data["attractionRemapMode"] = 3
        self._data["musclesFile"] = ""
        self._data["activationSmoothing"] = 1
        self._data["animatableRestMesh"] = False
        self._data["activationMode"] = 2
        self._data["maxCollisionSlidingDistance"] = 0.0
        self._data["keepCollisionOrientation"] = True
        self._data["computeCollisions"] = True
        self._data["bidirectionalActivation"] = False
        self._data["writeOutActivation"] = False
        self._data["initializeToAnimMesh"] = False
        self._data["attenuationMatrix"] = None
        self._data["collisionMeshMatrix"] = None
        self._data["collisionRestMeshMatrix"] = None
        self._data["deformMesh"] = None
        self._data["animMesh"] = None
        self._data["restMesh"] = None
        self._data["collisionMesh"] = None
        self._data["collisionRestMesh"] = None
        self._data["initShapePreservationAtStartTime"] = True
        self._data["initSlideCollisionAtStartTime"] = True
        self._data["attractForceMap"] = []
        self._data["collisionThresholdMultiplierMap"] = []
        self._data["compressionResistanceMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["globalDampingMap"] = []
        self._data["massMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["slideCollisionConstraintsMap"] = []

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnSimshape")
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode("AdnSimshape", name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type="AdnSimshape",
                                         name=self._data["name"],
                                         frontOfChain=True)[0]

            adn_locators.connect_to_debugger(node)
            self.setParameter("node", node)
            self.update()

    def update(self):
        super().update()
        node = self._data["node"]
        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            for attribute in attributes_list:
                if attribute in ["type", "geometry", "node", "name", "nodes", "connections"]:
                    continue
                elif attribute == "musclesFile":
                    muscle_file = self._data["musclesFile"]
                    if muscle_file:
                        cmds.setAttr("{0}.{1}".format(self.getName(), attribute), muscle_file, type="string")
                elif attribute == "gravityDirection":
                    cmds.setAttr("{0}.{1}".format(self.getName(), attribute),
                        self._data[attribute][0],
                        self._data[attribute][1],
                        self._data[attribute][2],
                        type="double3")
                elif attribute == "attenuationMatrix":
                    attenuation_matrix_name = self._data["attenuationMatrix"]
                    if attenuation_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attenuation_matrix_name)
                        adn_attenuation_matrix_attr = "{0}.attenuationMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_attenuation_matrix_attr, force=True)
                elif attribute == "collisionMeshMatrix":
                    collision_mesh_matrix_name = self._data["collisionMeshMatrix"]
                    if collision_mesh_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(collision_mesh_matrix_name)
                        adn_collision_mesh_matrix_attr = "{0}.collisionMeshMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_collision_mesh_matrix_attr, force=True)
                elif attribute == "collisionRestMeshMatrix":
                    collision_rest_mesh_matrix_name = self._data["collisionRestMeshMatrix"]
                    if collision_rest_mesh_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(collision_rest_mesh_matrix_name)
                        adn_collision_rest_mesh_matrix_attr = "{0}.collisionRestMeshMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_collision_rest_mesh_matrix_attr, force=True)
                elif attribute == "deformMesh":
                    deform_mesh_name = self._data["deformMesh"]
                    if deform_mesh_name:
                        maya_attachment_mesh = "{0}.outMesh".format(deform_mesh_name)
                        adn_deform_mesh_attr = "{0}.deformMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_deform_mesh_attr, force=True)
                elif attribute == "animMesh":
                    anim_mesh_name = self._data["animMesh"]
                    if anim_mesh_name:
                        maya_attachment_mesh = "{0}.outMesh".format(anim_mesh_name)
                        adn_anim_mesh_attr = "{0}.animMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_anim_mesh_attr, force=True)
                elif attribute == "restMesh":
                    rest_mesh_name = self._data["restMesh"]
                    if rest_mesh_name:
                        maya_attachment_mesh = "{0}.outMesh".format(rest_mesh_name)
                        adn_rest_mesh_attr = "{0}.restMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_rest_mesh_attr, force=True)
                elif attribute == "collisionMesh":
                    collision_mesh_name = self._data["collisionMesh"]
                    if collision_mesh_name:
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(collision_mesh_name)
                        adn_collision_mesh_attr = "{0}.collisionMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_collision_mesh_attr, force=True)
                elif attribute == "collisionRestMesh":
                    collision_rest_mesh_name = self._data["collisionRestMesh"]
                    if collision_rest_mesh_name:
                        maya_attachment_mesh = "{0}.worldMesh[0]".format(collision_rest_mesh_name)
                        adn_collision_rest_mesh_attr = "{0}.collisionRestMesh".format(node)
                        connect_attr(maya_attachment_mesh, adn_collision_rest_mesh_attr, force=True)
                elif attribute == "attractForceMap":
                    attract_force_weights = self._data["attractForceMap"]
                    for vertex_index in range(len(attract_force_weights)):
                        cmds.setAttr("{0}.attractForceList[0].attractForce[{1}]".format(node, vertex_index), attract_force_weights[vertex_index])
                elif attribute == "collisionThresholdMultiplierMap":
                    collision_threshold_multiplier_weights = self._data["collisionThresholdMultiplierMap"]
                    for vertex_index in range(len(collision_threshold_multiplier_weights)):
                        cmds.setAttr("{0}.collisionThresholdMultiplierList[0].collisionThresholdMultiplier[{1}]".format(node, vertex_index), collision_threshold_multiplier_weights[vertex_index])
                elif attribute == "compressionResistanceMap":
                    compression_resistance_weights = self._data["compressionResistanceMap"]
                    for vertex_index in range(len(compression_resistance_weights)):
                        cmds.setAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, vertex_index), compression_resistance_weights[vertex_index])
                elif attribute == "stretchingResistanceMap":
                    stretching_resistance_weights = self._data["stretchingResistanceMap"]
                    for vertex_index in range(len(stretching_resistance_weights)):
                        cmds.setAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, vertex_index), stretching_resistance_weights[vertex_index])
                elif attribute == "globalDampingMap":
                    global_damping_weights = self._data["globalDampingMap"]
                    for vertex_index in range(len(global_damping_weights)):
                        cmds.setAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, vertex_index), global_damping_weights[vertex_index])
                elif attribute == "massMap":
                    mass_weights = self._data["massMap"]
                    for vertex_index in range(len(mass_weights)):
                        cmds.setAttr("{0}.massList[0].mass[{1}]".format(node, vertex_index), mass_weights[vertex_index])
                elif attribute == "shapePreservationMap":
                    shape_preservation_weights = self._data["shapePreservationMap"]
                    for vertex_index in range(len(shape_preservation_weights)):
                        cmds.setAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, vertex_index), shape_preservation_weights[vertex_index])
                elif attribute == "slideCollisionConstraintsMap":
                    slide_collision_weights = self._data["slideCollisionConstraintsMap"]
                    for vertex_index in range(len(slide_collision_weights)):
                        cmds.setAttr("{0}.slideCollisionConstraintsList[0].slideCollisionConstraints[{1}]".format(node, vertex_index), slide_collision_weights[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False)
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)
                        else:
                            logging.debug("Attribute {0} has an incoming connection. Cannot set value to {1}".format(attribute, value))

            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameter_list = ["material", "triangulateMesh", "pointMassMode", "density",
                              "useCustomStiffness", "stiffness", "overrideShapePreservationStiffness",
                              "stiffnessShapePreservation", "distanceStiffnessOverride",
                              "shapeStiffnessOverride", "slideCollisionStiffnessOverride",
                              "globalMassMultiplier" ,"globalDampingMultiplier", "inertiaDamper",
                              "restLengthMultiplier", "compressionMultiplier", "stretchingMultiplier",
                              "attenuationVelocityFactor", "attractionMultiplier", "attractionRemapMode",
                              "musclesFile", "activationSmoothing", "writeOutActivation", "animatableRestMesh",
                              "activationMode", "maxCollisionSlidingDistance", "keepCollisionOrientation",
                              "computeCollisions", "bidirectionalActivation", "initializeToAnimMesh",
                              "initShapePreservationAtStartTime", "initSlideCollisionAtStartTime"]
            for parameter in parameter_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            # Attenuation matrix
            attenuation_matrix = cmds.listConnections("{0}.attenuationMatrix".format(node)) or []
            attenuation_matrix = attenuation_matrix[0] if attenuation_matrix else None
            self.setParameter("attenuationMatrix", attenuation_matrix)
            # Collision mesh matrix
            collision_mesh_matrix = cmds.listConnections("{0}.collisionMeshMatrix".format(node)) or []
            collision_mesh_matrix = collision_mesh_matrix[0] if collision_mesh_matrix else None
            self.setParameter("collisionMeshMatrix", collision_mesh_matrix)
            # Collision rest mesh matrix
            collision_rest_mesh_matrix = cmds.listConnections("{0}.collisionRestMeshMatrix".format(node)) or []
            collision_rest_mesh_matrix = collision_rest_mesh_matrix[0] if collision_rest_mesh_matrix else None
            self.setParameter("collisionRestMeshMatrix", collision_rest_mesh_matrix)

            # Deform Mesh
            deform_mesh = cmds.listConnections("{0}.deformMesh".format(node)) or []
            deform_mesh = deform_mesh[0] if deform_mesh else None
            self.setParameter("deformMesh", deform_mesh)
            # Anim Mesh
            anim_mesh = cmds.listConnections("{0}.animMesh".format(node)) or []
            anim_mesh = anim_mesh[0] if anim_mesh else None
            self.setParameter("animMesh", anim_mesh)
            # Rest Mesh
            rest_mesh = cmds.listConnections("{0}.restMesh".format(node)) or []
            rest_mesh = rest_mesh[0] if rest_mesh else None
            self.setParameter("restMesh", rest_mesh)
            # Collision Mesh
            collision_mesh = cmds.listConnections("{0}.collisionMesh".format(node)) or []
            collision_mesh = collision_mesh[0] if collision_mesh else None
            self.setParameter("collisionMesh", collision_mesh)
            # Collision Rest Mesh
            collision_rest_mesh = cmds.listConnections("{0}.collisionRestMesh".format(node)) or []
            collision_rest_mesh = collision_rest_mesh[0] if collision_rest_mesh else None
            self.setParameter("collisionRestMesh", collision_rest_mesh)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Attract Force Map
            attract_force_map = []
            for i in range(vertex_count):
                attract_force_map.append(cmds.getAttr("{0}.attractForceList[0].attractForce[{1}]".format(node, i)))
            self.setParameter("attractForceMap", attract_force_map)
            # Collision Threshold Multiplier Map
            collision_threshold_multiplier_map = []
            for i in range(vertex_count):
                collision_threshold_multiplier_map.append(cmds.getAttr("{0}.collisionThresholdMultiplierList[0].collisionThresholdMultiplier[{1}]".format(node, i)))
            self.setParameter("collisionThresholdMultiplierMap", collision_threshold_multiplier_map)
            # Compression Resistance Map
            compression_resistance_map = []
            for i in range(vertex_count):
                compression_resistance_map.append(cmds.getAttr("{0}.compressionResistanceList[0].compressionResistance[{1}]".format(node, i)))
            self.setParameter("compressionResistanceMap", compression_resistance_map)
            # Stretching Resistance Map
            stretching_resistance_map = []
            for i in range(vertex_count):
                stretching_resistance_map.append(cmds.getAttr("{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(node, i)))
            self.setParameter("stretchingResistanceMap", stretching_resistance_map)
            # Global Damping Map
            global_damping_map = []
            for i in range(vertex_count):
                global_damping_map.append(cmds.getAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(node, i)))
            self.setParameter("globalDampingMap", global_damping_map)
            # Mass Map
            mass_map = []
            for i in range(vertex_count):
                mass_map.append(cmds.getAttr("{0}.massList[0].mass[{1}]".format(node, i)))
            self.setParameter("massMap", mass_map)
            # Shape Preservation Map
            shape_preservation_map = []
            for i in range(vertex_count):
                shape_preservation_map.append(cmds.getAttr("{0}.shapePreservationList[0].shapePreservation[{1}]".format(node, i)))
            self.setParameter("shapePreservationMap", shape_preservation_map)
            # Slide Collision Constraints Map
            slide_collision_constraints_map = []
            for i in range(vertex_count):
                slide_collision_constraints_map.append(cmds.getAttr("{0}.slideCollisionConstraintsList[0].slideCollisionConstraints[{1}]".format(node, i)))
            self.setParameter("slideCollisionConstraintsMap", slide_collision_constraints_map)

            # Connections
            ignore_at_destination = ["deformMesh", "animMesh", "restMesh", "collisionMesh", "collisionRestMesh",
                                     "attenuationMatrix", "collisionMeshMatrix", "collisionRestMeshMatrix"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)


class AdnGlue(AdnSolverBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kGlue
        self._data["substeps"] = 1
        self._data["stiffness"] = 5000.0
        self._data["volumePreservation"] = 0.0
        self._data["bypass"] = False
        self._data["glueStiffnessOverride"] = -1.0
        self._data["softStiffnessOverride"] = -1.0
        self._data["distanceStiffnessOverride"] = -1.0
        self._data["shapeStiffnessOverride"] = -1.0
        self._data["pointMassMode"] = 0
        self._data["density"] = 1060.0
        self._data["globalMassMultiplier"] = 1.0
        self._data["triangulateMesh"] = False
        self._data["glueMultiplier"] = 1.0
        self._data["maxGlueDistance"] = 0.0
        self._data["compressionMultiplier"] = 1.0
        self._data["stretchingMultiplier"] = 1.0
        self._data["substepsInterpolationExponent"] = 1.0
        self._data["dynamic"] = False
        self._data["selfCollisions"] = False
        self._data["scIterations"] = 1
        self._data["scPointRadiusScale"] = 1.0
        self._data["scPointRadiusMode"] = 1
        self._data["scSearchRadius"] = -1.0
        self._data["inputs"] = []
        self._data["outputMesh"] = None
        self._data["gravity"] = 0.0
        self._data["globalDampingMultiplier"] = 0.0
        self._data["inertiaDamper"] = 0.0
        self._data["attenuationMatrix"] = None
        self._data["attenuationVelocityFactor"] = 1.0
        self._data["compressionResistanceMap"] = []
        self._data["stretchingResistanceMap"] = []
        self._data["glueResistanceMap"] = []
        self._data["maxGlueDistanceMultiplierMap"] = []
        self._data["shapePreservationMap"] = []
        self._data["massMap"] = []
        self._data["scWeightsMap"] = []
        self._data["scPointRadiusMultiplierMap"] = []
        self._data["softConstraintsMap"] = []
        self._data["globalDampingMap"] = []

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["substeps", "stiffness", "bypass", "volumePreservation", "glueStiffnessOverride",
                "softStiffnessOverride", "distanceStiffnessOverride", "shapeStiffnessOverride", "pointMassMode",
                "density", "globalMassMultiplier", "triangulateMesh", "glueMultiplier", "maxGlueDistance",
                "compressionMultiplier", "stretchingMultiplier", "globalDampingMultiplier", "inertiaDamper", 
                "substepsInterpolationExponent", "dynamic", "attenuationVelocityFactor", "selfCollisions",
                "scIterations", "scPointRadiusScale", "scPointRadiusMode", "scSearchRadius"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            # Build a unique list of inputs while preserving the order
            raw_glue_inputs = cmds.listConnections("{0}.inputs".format(node)) or []
            unique_glue_inputs = set()
            glue_inputs = []
            for input in raw_glue_inputs:
                if input not in unique_glue_inputs:
                    unique_glue_inputs.add(input)
                    glue_inputs.append(input)
            self.setParameter("inputs", glue_inputs)
            glue_output = cmds.listConnections("{0}.outputMesh".format(node), shapes=True)
            self.setParameter("outputMesh", glue_output)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["outputMesh"], vertex=True)
            # Compression Resistance Map
            compression_resistance_map = cmds.getAttr("{0}.compressionResistance".format(node))
            self.setParameter("compressionResistanceMap", compression_resistance_map)
            # Stretching Resistance Map
            stretching_resistance_map = cmds.getAttr("{0}.stretchingResistance".format(node))
            self.setParameter("stretchingResistanceMap", stretching_resistance_map)
            # Glue Resistance Map
            glue_resistance_map = cmds.getAttr("{0}.glueResistance".format(node))
            self.setParameter("glueResistanceMap", glue_resistance_map)
            # Max Glue Distance Multiplier Map
            max_glue_distance_multiplier_map = cmds.getAttr("{0}.maxGlueDistanceMultiplier".format(node))
            self.setParameter("maxGlueDistanceMultiplierMap", max_glue_distance_multiplier_map)
            # Shape Preservation Map
            shape_preservation_map = cmds.getAttr("{0}.shapePreservation".format(node))
            self.setParameter("shapePreservationMap", shape_preservation_map)
            # Mass Map
            mass_map = cmds.getAttr("{0}.mass".format(node))
            self.setParameter("massMap", mass_map)
            # Self-Collisions Weights Map
            sc_weights_map = cmds.getAttr("{0}.scWeights".format(node))
            self.setParameter("scWeightsMap", sc_weights_map)
            # Point Radius Multiplier Map
            point_radius_mult_map = cmds.getAttr("{0}.scPointRadiusMultiplier".format(node))
            self.setParameter("scPointRadiusMultiplierMap", point_radius_mult_map)
            # Soft Constraints Map
            soft_constraints_map = cmds.getAttr("{0}.softConstraints".format(node))
            self.setParameter("softConstraintsMap", soft_constraints_map)
            # Global Damping Map
            global_damping_map = cmds.getAttr("{0}.globalDamping".format(node))
            self.setParameter("globalDampingMap", global_damping_map)

            # Attenuation matrix
            attenuation_matrix = cmds.listConnections("{0}.attenuationMatrix".format(node)) or []
            attenuation_matrix = attenuation_matrix[0] if attenuation_matrix else None
            self.setParameter("attenuationMatrix", attenuation_matrix)
            
            # Connections
            ignore_at_destination = ["inputs", "outputMesh"]
            ignore_at_source = ["outputMesh"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination,
                                                                     ignore_at_source=ignore_at_source)
    
    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False
            
    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnGlue")
            if node:
                node = node[0]
            else:
                node = cmds.createNode("AdnGlue", name=self._data["name"])

            adn_locators.connect_to_debugger(node)
            self.setParameter("node", node)
            self.update()
    
    def update(self):
        super().update()
        node = self._data["node"]
        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            for attribute in attributes_list:
                if attribute in ["type", "node", "name", "nodes", "connections", "geometry", 
                                 "stiffnessMultiplier", "material"]:
                    continue
                elif attribute == "gravityDirection":
                    cmds.setAttr("{0}.{1}".format(self.getName(), attribute),
                        self._data[attribute][0],
                        self._data[attribute][1],
                        self._data[attribute][2],
                        type="double3")
                elif attribute == "inputs":
                    inputs_data = self._data["inputs"]
                    for input_index in range(len(inputs_data)):
                        input_name = inputs_data[input_index]
                        maya_input_mesh = "{0}.worldMesh[0]".format(input_name)
                        maya_input_matrix = "{0}.worldMatrix[0]".format(input_name)
                        adn_inputs_attr = "{0}.inputs".format(node)
                        adn_input_mesh = "{0}[{1}].inputMesh".format(adn_inputs_attr, input_index)
                        adn_input_matrix = "{0}[{1}].inputMatrix".format(adn_inputs_attr, input_index)
                        connect_attr(maya_input_mesh, adn_input_mesh, force=True)
                        connect_attr(maya_input_matrix, adn_input_matrix, force=True)
                elif attribute == "outputMesh":
                    if not self._data["outputMesh"]:
                        logging.error("{0}.outputMesh could not be set because it is missing in the JSON file.".format(node))
                        continue
                    outputs_data = self._data["outputMesh"]
                    for output_index in range(len(outputs_data)):
                        output_name = outputs_data[output_index]
                        maya_output_mesh = "{0}.inMesh".format(output_name)
                        adn_output_mesh = "{0}.outputMesh".format(node)
                        if not cmds.objExists(maya_output_mesh):
                            logging.error("{0}.outputMesh could not be connected to {1} because no object matches that name.".format(node, maya_output_mesh))
                            continue
                        connect_attr(adn_output_mesh, maya_output_mesh, force=True)
                elif attribute == "attenuationMatrix":
                    attenuation_matrix_name = self._data["attenuationMatrix"]
                    if attenuation_matrix_name:
                        maya_attachment_matrix = "{0}.worldMatrix[0]".format(attenuation_matrix_name)
                        adn_attenuation_matrix_attr = "{0}.attenuationMatrix".format(node)
                        connect_attr(maya_attachment_matrix, adn_attenuation_matrix_attr, force=True)
                elif attribute == "compressionResistanceMap":
                    weights = self._data["compressionResistanceMap"]
                    cmds.setAttr("{0}.compressionResistance".format(node), weights, type="doubleArray")
                elif attribute == "stretchingResistanceMap":
                    weights = self._data["stretchingResistanceMap"]
                    cmds.setAttr("{0}.stretchingResistance".format(node), weights, type="doubleArray")
                elif attribute == "glueResistanceMap":
                    weights = self._data["glueResistanceMap"]
                    cmds.setAttr("{0}.glueResistance".format(node), weights, type="doubleArray")
                elif attribute == "maxGlueDistanceMultiplierMap":
                    weights = self._data["maxGlueDistanceMultiplierMap"]
                    cmds.setAttr("{0}.maxGlueDistanceMultiplier".format(node), weights, type="doubleArray")
                elif attribute == "shapePreservationMap":
                    weights = self._data["shapePreservationMap"]
                    cmds.setAttr("{0}.shapePreservation".format(node), weights, type="doubleArray")
                elif attribute == "massMap":
                    weights = self._data["massMap"]
                    cmds.setAttr("{0}.mass".format(node), weights, type="doubleArray")
                elif attribute == "scWeightsMap":
                    weights = self._data["scWeightsMap"]
                    cmds.setAttr("{0}.scWeights".format(node), weights, type="doubleArray")
                elif attribute == "scPointRadiusMultiplierMap":
                    weights = self._data["scPointRadiusMultiplierMap"]
                    cmds.setAttr("{0}.scPointRadiusMultiplier".format(node), weights, type="doubleArray")
                elif attribute == "softConstraintsMap":
                    weights = self._data["softConstraintsMap"]
                    cmds.setAttr("{0}.softConstraints".format(node), weights, type="doubleArray")
                elif attribute == "globalDampingMap":
                    weights = self._data["globalDampingMap"]
                    cmds.setAttr("{0}.globalDamping".format(node), weights, type="doubleArray")
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False) or []
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)

            self._failed_connections = self.getRig().setConnections(self._data["connections"])


class AdnSkinMerge(AdnDeformerBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSkinMerge
        self._data["initializationTime"] = 0
        self._data["animList"] = []
        self._data["simList"] = []
        self._data["blendMap"] = []

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["initializationTime"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)
            anim_inputs = list(set(cmds.listConnections("{0}.animList".format(node))))
            self.setParameter("animList", anim_inputs)
            sim_inputs = list(set(cmds.listConnections("{0}.simList".format(node))))
            self.setParameter("simList", sim_inputs)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Compression Resistance Map
            blend_map = []
            for vertex_index in range(vertex_count):
                blend_map.append(cmds.getAttr("{0}.blendList[0].blend[{1}]".format(node, vertex_index)))
            self.setParameter("blendMap", blend_map)

            # Connections
            ignore_at_destination = ["animList", "simList"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)
    
    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the solver.".format(parameter))
                return False
            
    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnSkinMerge")
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode("AdnSkinMerge", name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type="AdnSkinMerge",
                                         name=self._data["name"],
                                         frontOfChain=True)[0]
            self.setParameter("node", node)
            self.update()
    
    def update(self):
        super().update()
        node = self._data["node"]

        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            for attribute in attributes_list:
                if attribute in ["type", "node", "name", "nodes", "connections", "geometry",
                                 "stiffnessMultiplier", "spaceScaleMode", "gravity",
                                 "gravityDirection", "material"]:
                    continue
                elif attribute == "simList":
                    simList_data = self._data["simList"]
                    for input_index in range(len(simList_data)):
                        input_name = simList_data[input_index]
                        maya_input_mesh = "{0}.worldMesh[0]".format(input_name)
                        maya_input_matrix = "{0}.worldMatrix[0]".format(input_name)
                        adn_inputs_attr = "{0}.simList".format(node)
                        adn_input_mesh = "{0}[{1}].simWorldMesh".format(adn_inputs_attr, input_index)
                        adn_input_matrix = "{0}[{1}].simWorldMatrix".format(adn_inputs_attr, input_index)
                        connect_attr(maya_input_mesh, adn_input_mesh, force=True)
                        connect_attr(maya_input_matrix, adn_input_matrix, force=True)
                elif attribute == "animList":
                    animList_data = self._data["animList"]
                    for input_index in range(len(animList_data)):
                        input_name = animList_data[input_index]
                        maya_input_mesh = "{0}.worldMesh[0]".format(input_name)
                        maya_input_matrix = "{0}.worldMatrix[0]".format(input_name)
                        adn_inputs_attr = "{0}.animList".format(node)
                        adn_input_mesh = "{0}[{1}].animWorldMesh".format(adn_inputs_attr, input_index)
                        adn_input_matrix = "{0}[{1}].animWorldMatrix".format(adn_inputs_attr, input_index)
                        connect_attr(maya_input_mesh, adn_input_mesh, force=True)
                        connect_attr(maya_input_matrix, adn_input_matrix, force=True)
                elif attribute == "blendMap":
                    weights = self._data["blendMap"]
                    max_vertex_count = min(vertex_count, len(weights))
                    for vertex_index in range(max_vertex_count) :
                        cmds.setAttr("{0}.blendList[0].blend[{1}]".format(node, vertex_index), weights[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False) or []
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)

            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)


class AdnRelax(AdnDeformerBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kRelax
        self._data["iterations"] = 0
        self._data["pin"] = False
        self._data["smooth"] = 0.5
        self._data["relax"] = 0.5
        self._data["pushInRatio"] = 0.0
        self._data["pushInThreshold"] = -1.0
        self._data["pushOutRatio"] = 0.0
        self._data["pushOutThreshold"] = -1.0
        self._data["pushInRatioMultiplierMap"] = []
        self._data["pushOutRatioMultiplierMap"] = []
        self._data["smoothMultiplierMap"] = []
        self._data["relaxMultiplierMap"] = []

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            parameters_list = ["iterations", "pin", "smooth", "relax",
                "pushInRatio", "pushInThreshold", "pushOutRatio", "pushOutThreshold"]
            for parameter in parameters_list:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                self.setParameter(parameter, value)

            # Getting Maps
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            # Push-In Ratio Multiplier Map
            push_in_ratio_map = []
            for vertex_index in range(vertex_count):
                push_in_ratio_map.append(cmds.getAttr("{0}.pushInRatioMultiplierList[0].pushInRatioMultiplier[{1}]".format(node, vertex_index)))
            self.setParameter("pushInRatioMultiplierMap", push_in_ratio_map)
            # Push-Out Ratio Multiplier Map
            push_out_ratio_map = []
            for vertex_index in range(vertex_count):
                push_out_ratio_map.append(cmds.getAttr("{0}.pushOutRatioMultiplierList[0].pushOutRatioMultiplier[{1}]".format(node, vertex_index)))
            self.setParameter("pushOutRatioMultiplierMap", push_out_ratio_map)

            # Smooth Multiplier Map
            smooth_map = []
            for vertex_index in range(vertex_count):
                smooth_map.append(cmds.getAttr("{0}.smoothMultiplierList[0].smoothMultiplier[{1}]".format(node, vertex_index)))
            self.setParameter("smoothMultiplierMap", smooth_map)

            # Relax Multiplier Map
            relax_map = []
            for vertex_index in range(vertex_count):
                relax_map.append(cmds.getAttr("{0}.relaxMultiplierList[0].relaxMultiplier[{1}]".format(node, vertex_index)))
            self.setParameter("relaxMultiplierMap", relax_map)

            # Connections
            self._data["connections"] = self.getRig().getConnections(node)
    
    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not compatible with the deformer.".format(parameter))
                return False
            
    def build(self):
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(self._data["name"], type="AdnRelax")
            if node:
                node = node[0]
            else:
                create_as_node = deformable_chain_exists(self._data["geometry"],
                                                         self._data["name"],
                                                         self._data["connections"])
                # There is a deformable chain already, create as standalone node
                if create_as_node:
                    node = cmds.createNode("AdnRelax", name=self._data["name"])
                # There is no deformable chain yet, create as deformer
                else:
                    node = cmds.deformer(self._data["geometry"],
                                         type="AdnRelax",
                                         name=self._data["name"],
                                         frontOfChain=False)[0]

            self.setParameter("node", node)
            self.update()
    
    def update(self):
        super().update()
        node = self._data["node"]

        attributes_list = self._data.keys()
        if self.getHost() == AdnHost.kMaya:
            vertex_count = cmds.polyEvaluate(self._data["geometry"], vertex=True)
            for attribute in attributes_list:
                if attribute in ["type", "node", "name", "nodes", "connections", "geometry"]:
                    continue
                elif attribute == "pushInRatioMultiplierMap":
                    attribute_map = self._data["pushInRatioMultiplierMap"]
                    max_vertex_count = min(vertex_count, len(attribute_map))
                    for vertex_index in range(max_vertex_count) :
                        cmds.setAttr("{0}.pushInRatioMultiplierList[0].pushInRatioMultiplier[{1}]".format(node, vertex_index), attribute_map[vertex_index])
                elif attribute == "pushOutRatioMultiplierMap":
                    attribute_map = self._data["pushOutRatioMultiplierMap"]
                    max_vertex_count = min(vertex_count, len(attribute_map))
                    for vertex_index in range(max_vertex_count) :
                        cmds.setAttr("{0}.pushOutRatioMultiplierList[0].pushOutRatioMultiplier[{1}]".format(node, vertex_index), attribute_map[vertex_index])
                elif attribute == "smoothMultiplierMap":
                    attribute_map = self._data["smoothMultiplierMap"]
                    max_vertex_count = min(vertex_count, len(attribute_map))
                    for vertex_index in range(max_vertex_count) :
                        cmds.setAttr("{0}.smoothMultiplierList[0].smoothMultiplier[{1}]".format(node, vertex_index), attribute_map[vertex_index])
                elif attribute == "relaxMultiplierMap":
                    attribute_map = self._data["relaxMultiplierMap"]
                    max_vertex_count = min(vertex_count, len(attribute_map))
                    for vertex_index in range(max_vertex_count) :
                        cmds.setAttr("{0}.relaxMultiplierList[0].relaxMultiplier[{1}]".format(node, vertex_index), attribute_map[vertex_index])
                else:
                    value = self._data[attribute]
                    node_attribute = "{0}.{1}".format(self.getName(), attribute)
                    if cmds.attributeQuery(attribute, node=node, exists=True):
                        attribute_connections = cmds.listConnections(node_attribute, source=True, destination=False) or []
                        if attribute_connections is None or len(attribute_connections) == 0:
                            logging.debug("Setting attribute {0} with value {1}".format(attribute, value))
                            cmds.setAttr(node_attribute, value)

            # Connections
            # Check if the node is receiving an inputGeometry
            # If so, we ignore that connections
            input_shape = cmds.listConnections("{0}.input[0].inputGeometry".format(node), source=True) or []
            ignore_at_destination = [] if not input_shape else ["input"]
            self._failed_connections = self.getRig().setConnections(self._data["connections"],
                                                                    node=node,
                                                                    ignore_at_destination=ignore_at_destination)


class AdnSensorBase(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "name": None,
            "sensorName": "",
            "type": AdnTypes.kNone,
            "nodes": [],
            "connections": [],
            "instantInputMin": 0.0,
            "instantInputMax": 0.0,
            "instantOutputMin": 0.0,
            "instantOutputMax": 0.0,
            "scale": 1.0,
            "drawOutput": 0,
            "startTime": 0.0,
            "timeScale": 1.0
        }
        self._failed_connections = []
        if self not in rig.getSensors():
            rig.addSensor(self)

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        available_parameters = ["name", "sensorName", "type",
            "instantInputMin", "instantInputMax", 
            "instantOutputMin", "instantOutputMax",
            "scale", "drawOutput", "startTime", "timeScale"]
        if parameter in available_parameters:
            self._data[parameter] = value
            return True
        return False

    def clear(self, force=False):
        if self._rig.getHost() == AdnHost.kMaya:
            for connection in self._connections:
                connection_start = "{0}.{1}".format(connection.start_node, connection.start_attribute)
                connection_end = "{0}.{1}".format(connection.end_node, connection.end_attribute)
                cmds.disconnectAttr(connection_start, connection_end)
            for node in self._nodes:
                cmds.delete(node)
            cmds.delete(self._node)

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self._failed_connections = []
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        if self.getHost() == AdnHost.kMaya:
            # Draw attributes
            scale = cmds.getAttr("{0}.scale".format(node))
            self.setParameter("scale", scale)
            draw_output = cmds.getAttr("{0}.drawOutput".format(node))
            self.setParameter("drawOutput", draw_output)

    def remapSettingsFromNode(self, node, plug_name, labels, sensor_type):
        remap_node = cmds.listConnections("{0}.{1}".format(node, plug_name),
            source=True, destination=False) or []
        if not remap_node:
            return None

        remap_node = remap_node[0]
        param_label, sensor_label = labels

        # The remap settings are provided by a remapValue Maya node
        if cmds.nodeType(remap_node) == "remapValue":
            input_min = cmds.getAttr("{0}.inputMin".format(remap_node))
            input_max = cmds.getAttr("{0}.inputMax".format(remap_node))
            output_min = cmds.getAttr("{0}.outputMin".format(remap_node))
            output_max = cmds.getAttr("{0}.outputMax".format(remap_node))
            self.setParameter("{0}RangeInputMin".format(param_label), input_min)
            self.setParameter("{0}RangeInputMax".format(param_label), input_max)
            self.setParameter("{0}RangeOutputMin".format(param_label), output_min)
            self.setParameter("{0}RangeOutputMax".format(param_label), output_max)
        # The remap settings are provided by a sensor node
        elif cmds.nodeType(remap_node) == sensor_type:
            input_min = cmds.getAttr("{0}.inputMin{1}".format(remap_node, sensor_label))
            input_max = cmds.getAttr("{0}.inputMax{1}".format(remap_node, sensor_label))
            output_min = cmds.getAttr("{0}.outputMin{1}".format(remap_node, sensor_label))
            output_max = cmds.getAttr("{0}.outputMax{1}".format(remap_node, sensor_label))
            self.setParameter("{0}RangeInputMin".format(param_label), input_min)
            self.setParameter("{0}RangeInputMax".format(param_label), input_max)
            self.setParameter("{0}RangeOutputMin".format(param_label), output_min)
            self.setParameter("{0}RangeOutputMax".format(param_label), output_max)

        return remap_node

    def inputJointsFromNode(self, node, position_plug_name, matrix_plug_name, label):
        sensor_joint = None
        sensor_decompose = cmds.listConnections("{0}.{1}".format(node, position_plug_name),
            source=True, destination=False) or []
        if sensor_decompose:
            sensor_joint = cmds.listConnections("{0}.inputMatrix".format(sensor_decompose[0]),
                source=True, destination=False) or []
            if sensor_joint:
                self.setParameter(label, sensor_joint[0])
        if not sensor_joint:
            sensor_joint = cmds.listConnections("{0}.{1}".format(node, matrix_plug_name),
                source=True, destination=False) or []
            if sensor_joint:
                self.setParameter(label, sensor_joint[0])

    def updateMatrixInput(self, node, locator_name, sensor_name, matrix_plug_name):
        if node:
            connect_attr("{0}.worldMatrix[0]".format(node),
                         "{0}.{1}".format(locator_name, matrix_plug_name),
                         force=True)
            if sensor_name:
                connect_attr("{0}.worldMatrix[0]".format(node),
                             "{0}.{1}".format(sensor_name, matrix_plug_name),
                             force=True)

    def update(self):
        self.preUpdate()

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True, destination=False, plugs=True, connections=True) or []
            if self._data["sensorName"]:
                sensor_node = self._data["sensorName"]
                input_connections += cmds.listConnections(sensor_node, source=True, destination=False, plugs=True, connections=True)  or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}".format(source, destination))

    def getFailedConnections(self):
        return self._failed_connections


class AdnSensorPosition(AdnSensorBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSensorPosition
        self._data["sensorPosition"] = None
        self._data["spaceScale"] = 1.0
        self._data["velRangeInputMin"] = 0.0
        self._data["velRangeInputMax"] = 10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = -10.0
        self._data["accelRangeInputMax"] = 10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0

    def reset(self):
        super().reset()
        self._data["sensorPosition"] = None
        self._data["spaceScale"] = 1.0
        self._data["velRangeInputMin"] = 0.0
        self._data["velRangeInputMax"] = 10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = -10.0
        self._data["accelRangeInputMax"] = 10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0

    def fromDict(self, in_dictionary):        
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters
        
    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Locator: velocity activation and input remap
            vel_instant_range_node = self.remapSettingsFromNode(node, "activationVelocity", ("vel", "Velocity"), "AdnSensorPosition")
            # Locator: acceleration activation and input remap
            self.remapSettingsFromNode(node, "activationAcceleration", ("accel", "Acceleration"), "AdnSensorPosition")
            # Locator: position or matrix
            self.inputJointsFromNode(node, "position", "positionMatrix", "sensorPosition")
            # Sensor: gather from the activation distance plug upstream
            if vel_instant_range_node:
                if cmds.nodeType(vel_instant_range_node) == "AdnSensorPosition":
                    sensor_node = vel_instant_range_node
                elif cmds.nodeType(vel_instant_range_node) == "AdnRemap":
                    sensor_node = cmds.listConnections("{0}.input".format(vel_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]
                else:
                    sensor_node = cmds.listConnections("{0}.inputValue".format(vel_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]

                if sensor_node:
                    self.setParameter("sensorName", sensor_node)
                    # Time attributes
                    start_time = cmds.getAttr("{0}.startTime".format(sensor_node))
                    self.setParameter("startTime", start_time)
                    # Scale attributes
                    time_scale = cmds.getAttr("{0}.timeScale".format(sensor_node))
                    self.setParameter("timeScale", time_scale)
                    space_scale = cmds.getAttr("{0}.spaceScale".format(sensor_node))
                    self.setParameter("spaceScale", space_scale)

            # Connections
            ignore_at_destination = ["position", "positionMatrix", "activationVelocity", "activationAcceleration"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            position_node = self._data["sensorPosition"]

            if not position_node:
                logging.error("AdnLocatorPosition creation aborted \"{0}\": input position node required but not provided."
                              "".format(self._data["name"]))
                return

            # Locator: gather or create
            locator_name = self._data["name"]
            locator_node = cmds.ls(locator_name, type="AdnLocatorPosition")
            if not locator_node:
                cmds.select([position_node])
                new_locator_shape = adn_locators.create_locator_position()
                locator_transform = cmds.listRelatives(new_locator_shape, parent=True)[0]
                transform_name = "{0}{1}".format(
                    locator_name.rpartition("Shape")[0],
                    locator_name.rpartition("Shape")[2])
                cmds.rename(locator_transform, transform_name)

            # Sensor: gather or create
            sensor_name = self._data["sensorName"]
            new_sensor = None
            # If the sensor was not exported (empty name) don't build it
            if sensor_name:
                new_sensor = cmds.ls(sensor_name, type="AdnSensorPosition")
                if not new_sensor:
                    new_sensor = cmds.createNode("AdnSensorPosition", name=sensor_name)
                else:
                    new_sensor = new_sensor[0]

            self.update()

    def update(self):
        super().update()
        if self.getHost() == AdnHost.kMaya:
            position_node = self._data["sensorPosition"]
            locator_name = self._data["name"]
            sensor_name = self._data["sensorName"]

            # Locator and sensor: update start matrix
            self.updateMatrixInput(position_node, locator_name, sensor_name, "positionMatrix")

            # Locator: draw attributes
            cmds.setAttr("{0}.scale".format(locator_name), self._data["scale"])
            cmds.setAttr("{0}.drawOutput".format(locator_name), self._data["drawOutput"])

            if sensor_name:
                # Sensor: time attributes
                cmds.setAttr("{0}.startTime".format(sensor_name), self._data["startTime"])
                connect_attr("time1.outTime", "{0}.currentTime".format(sensor_name), force=True)
                # Sensor: scale attributes
                cmds.setAttr("{0}.spaceScale".format(sensor_name), self._data["spaceScale"])
                cmds.setAttr("{0}.timeScale".format(sensor_name), self._data["timeScale"])

                # Sensor: connect sensor to locator
                connect_attr("{0}.outVelocityRemap".format(sensor_name),
                             "{0}.activationVelocity".format(locator_name), force=True)
                connect_attr("{0}.outAccelerationRemap".format(sensor_name),
                             "{0}.activationAcceleration".format(locator_name), force=True)

                # Remappers: min/max ranges
                attributes_map = {
                    "accel": "Acceleration",
                    "vel": "Velocity"
                }
                for key in attributes_map.keys():
                    cmds.setAttr("{0}.inputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMin".format(key)])
                    cmds.setAttr("{0}.inputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMax".format(key)])
                    cmds.setAttr("{0}.outputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMin".format(key)])
                    cmds.setAttr("{0}.outputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMax".format(key)])

            self._failed_connections = self.getRig().setConnections(self._data["connections"])

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not "
                                    "compatible with the sensor.".format(parameter))
                return False
            return True


class AdnSensorDistance(AdnSensorBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSensorDistance
        self._data["sensorStart"] = None
        self._data["sensorEnd"] = None
        self._data["spaceScale"] = 1.0
        self._data["distanceRangeInputMin"] = 1.0
        self._data["distanceRangeInputMax"] = 0.0
        self._data["distanceRangeOutputMin"] = 0.0
        self._data["distanceRangeOutputMax"] = 1.0
        self._data["velRangeInputMin"] = -10.0
        self._data["velRangeInputMax"] = 10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = -10.0
        self._data["accelRangeInputMax"] = 10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0
        
    def reset(self):
        super().reset()
        self._data["sensorStart"] = None
        self._data["sensorEnd"] = None
        self._data["spaceScale"] = 1.0
        self._data["distanceRangeInputMin"] = 1.0
        self._data["distanceRangeInputMax"] = 0.0
        self._data["distanceRangeOutputMin"] = 0.0
        self._data["distanceRangeOutputMax"] = 1.0
        self._data["velRangeInputMin"] = -10.0
        self._data["velRangeInputMax"] = 10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = -10.0
        self._data["accelRangeInputMax"] = 10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0
        
    def fromDict(self, in_dictionary):        
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Locator: distance activation and input remap
            distance_instant_range_node = self.remapSettingsFromNode(node, "activationDistance", ("distance", "Distance"), "AdnSensorDistance")
            # Locator: velocity activation and input remap
            self.remapSettingsFromNode(node, "activationVelocity", ("vel", "Velocity"), "AdnSensorDistance")
            # Locator: acceleration activation and input remap
            self.remapSettingsFromNode(node, "activationAcceleration", ("accel", "Acceleration"), "AdnSensorDistance")
            # Locator: start position or matrix
            self.inputJointsFromNode(node, "startPosition", "startMatrix", "sensorStart")
            # Locator: end position or matrix
            self.inputJointsFromNode(node, "endPosition", "endMatrix", "sensorEnd")
            # Sensor: gather from the activation distance plug upstream
            if distance_instant_range_node:
                if cmds.nodeType(distance_instant_range_node) == "AdnSensorDistance":
                    sensor_node = distance_instant_range_node
                elif cmds.nodeType(distance_instant_range_node) == "AdnRemap":
                    sensor_node = cmds.listConnections("{0}.input".format(distance_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]
                else:
                    sensor_node = cmds.listConnections("{0}.inputValue".format(distance_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]

                if sensor_node:
                    self.setParameter("sensorName", sensor_node)
                    # Time attributes
                    start_time = cmds.getAttr("{0}.startTime".format(sensor_node))
                    self.setParameter("startTime", start_time)
                    # Scale attributes
                    time_scale = cmds.getAttr("{0}.timeScale".format(sensor_node))
                    self.setParameter("timeScale", time_scale)
                    space_scale = cmds.getAttr("{0}.spaceScale".format(sensor_node))
                    self.setParameter("spaceScale", space_scale)

            # Connections
            ignore_at_destination = ["startPosition", "endPosition", "startMatrix", "endMatrix", "activationDistance", "activationVelocity", "activationAcceleration"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            start_node = self._data["sensorStart"]
            end_node = self._data["sensorEnd"]

            if not start_node or not end_node:
                logging.error("AdnLocatorDistance creation aborted \"{0}\": input start and end nodes required but not provided."
                              "".format(self._data["name"]))
                return

            # Locator: gather or create
            locator_name = self._data["name"]
            locator_node = cmds.ls(locator_name, type="AdnLocatorDistance")
            if not locator_node:
                cmds.select([start_node, end_node])
                new_locator_shape = adn_locators.create_locator_distance()
                locator_transform = cmds.listRelatives(new_locator_shape, parent=True)[0]
                transform_name = "{0}{1}".format(
                    locator_name.rpartition("Shape")[0],
                    locator_name.rpartition("Shape")[2])
                cmds.rename(locator_transform, transform_name)

            # Sensor: gather or create
            sensor_name = self._data["sensorName"]
            new_sensor = None
            # If the sensor was not exported (empty name) don't build it
            if sensor_name:
                new_sensor = cmds.ls(sensor_name, type="AdnSensorDistance")
                if not new_sensor:
                    new_sensor = cmds.createNode("AdnSensorDistance", name=sensor_name)
                else:
                    new_sensor = new_sensor[0]

            self.update()

    def update(self):
        super().update()
        if self.getHost() == AdnHost.kMaya:
            start_node = self._data["sensorStart"]
            end_node = self._data["sensorEnd"]
            locator_name = self._data["name"]
            sensor_name = self._data["sensorName"]

            # Locator and sensor: update start matrix
            self.updateMatrixInput(start_node, locator_name, sensor_name, "startMatrix")
            # Locator and sensor: update end matrix
            self.updateMatrixInput(end_node, locator_name, sensor_name, "endMatrix")

            # Locator: draw attributes
            cmds.setAttr("{0}.scale".format(locator_name), self._data["scale"])
            cmds.setAttr("{0}.drawOutput".format(locator_name), self._data["drawOutput"])

            if sensor_name:
                # Sensor: time attributes
                cmds.setAttr("{0}.startTime".format(sensor_name), self._data["startTime"])
                connect_attr("time1.outTime", "{0}.currentTime".format(sensor_name), force=True)
                # Sensor: scale attributes
                cmds.setAttr("{0}.spaceScale".format(sensor_name), self._data["spaceScale"])
                cmds.setAttr("{0}.timeScale".format(sensor_name), self._data["timeScale"])

                # Sensor: connect sensor to locator
                connect_attr("{0}.outDistanceRemap".format(sensor_name),
                             "{0}.activationDistance".format(locator_name), force=True)
                connect_attr("{0}.outVelocityRemap".format(sensor_name),
                             "{0}.activationVelocity".format(locator_name), force=True)
                connect_attr("{0}.outAccelerationRemap".format(sensor_name),
                             "{0}.activationAcceleration".format(locator_name), force=True)

                # Remappers: min/max ranges
                attributes_map = {
                    "accel": "Acceleration",
                    "vel": "Velocity",
                    "distance": "Distance"
                }
                for key in attributes_map.keys():
                    cmds.setAttr("{0}.inputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMin".format(key)])
                    cmds.setAttr("{0}.inputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMax".format(key)])
                    cmds.setAttr("{0}.outputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMin".format(key)])
                    cmds.setAttr("{0}.outputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMax".format(key)])

            self._failed_connections = self.getRig().setConnections(self._data["connections"])

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not "
                                    "compatible with the sensor.".format(parameter))
                return False
            return True


class AdnSensorRotation(AdnSensorBase):
    def __init__(self, rig):
        super().__init__(rig)
        self._data["type"] = AdnTypes.kSensorAngle
        self._data["sensorStart"] = None
        self._data["sensorMid"] = None
        self._data["sensorEnd"] = None
        self._data["angleRangeInputMin"] = math.pi
        self._data["angleRangeInputMax"] = 0.0
        self._data["angleRangeOutputMin"] = 0.0
        self._data["angleRangeOutputMax"] = 1.0
        self._data["velRangeInputMin"] = 10.0
        self._data["velRangeInputMax"] = -10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = 10.0
        self._data["accelRangeInputMax"] = -10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0
    
    def reset(self):
        super().reset()
        self._data["sensorStart"] = None
        self._data["sensorMid"] = None
        self._data["sensorEnd"] = None
        self._data["angleRangeInputMin"] = math.pi
        self._data["angleRangeInputMax"] = 0.0
        self._data["angleRangeOutputMin"] = 0.0
        self._data["angleRangeOutputMax"] = 1.0
        self._data["velRangeInputMin"] = 10.0
        self._data["velRangeInputMax"] = -10.0
        self._data["velRangeOutputMin"] = 0.0
        self._data["velRangeOutputMax"] = 1.0
        self._data["accelRangeInputMin"] = 10.0
        self._data["accelRangeInputMax"] = -10.0
        self._data["accelRangeOutputMin"] = 0.0
        self._data["accelRangeOutputMax"] = 1.0

    def fromDict(self, in_dictionary):        
        self.reset()
        set_parameters = super().fromDict(in_dictionary)
        remaining_parameters = list(set(in_dictionary.keys()).difference(set(set_parameters)))
        for parameter in remaining_parameters:
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self.setNode(node)
        super().fromNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Locator: angle activation and input remap
            angle_instant_range_node = self.remapSettingsFromNode(node, "activationAngle", ("angle", "Angle"), "AdnSensorRotation")
            # Locator: velocity activation and input remap
            self.remapSettingsFromNode(node, "activationVelocity", ("vel", "Velocity"), "AdnSensorRotation")
            # Locator: acceleration activation and input remap
            self.remapSettingsFromNode(node, "activationAcceleration", ("accel", "Acceleration"), "AdnSensorRotation")
            # Locator: start position or matrix
            self.inputJointsFromNode(node, "startPosition", "startMatrix", "sensorStart")
            # Locator: mid position or matrix
            self.inputJointsFromNode(node, "midPosition", "midMatrix", "sensorMid")
            # Locator: end position or matrix
            self.inputJointsFromNode(node, "endPosition", "endMatrix", "sensorEnd")
            # Sensor: gather from the activation angle plug upstream
            if angle_instant_range_node:
                if cmds.nodeType(angle_instant_range_node) == "AdnSensorRotation":
                    sensor_node = angle_instant_range_node
                elif cmds.nodeType(angle_instant_range_node) == "AdnRemap":
                    sensor_node = cmds.listConnections("{0}.input".format(angle_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]
                else:
                    sensor_node = cmds.listConnections("{0}.inputValue".format(angle_instant_range_node))
                    if sensor_node:
                        sensor_node = sensor_node[0]

                if sensor_node:
                    self.setParameter("sensorName", sensor_node)
                    # Time attributes
                    start_time = cmds.getAttr("{0}.startTime".format(sensor_node))
                    self.setParameter("startTime", start_time)
                    # Scale attributes
                    time_scale = cmds.getAttr("{0}.timeScale".format(sensor_node))
                    self.setParameter("timeScale", time_scale)

            # Connections
            ignore_at_destination = ["startPosition", "midPosition", "endPosition", "startMatrix", "midMatrix",
                                     "endMatrix", "activationAngle", "activationVelocity", "activationAcceleration"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)

    def build(self):
        if self.getHost() == AdnHost.kMaya:
            start_node = self._data["sensorStart"]
            mid_node = self._data["sensorMid"]
            end_node = self._data["sensorEnd"]

            if not start_node or not mid_node or not end_node:
                logging.error("AdnLocatorRotation creation aborted \"{0}\": input start, mid and end nodes required but not provided."
                              "".format(self._data["name"]))
                return

            # Locator: gather or create
            locator_name = self._data["name"]
            locator_node = cmds.ls(locator_name, type="AdnLocatorRotation")
            if not locator_node:
                cmds.select([start_node, mid_node, end_node])
                new_locator_shape = adn_locators.create_locator_rotation()
                locator_transform = cmds.listRelatives(new_locator_shape, parent=True)[0]
                transform_name = "{0}{1}".format(
                    locator_name.rpartition("Shape")[0],
                    locator_name.rpartition("Shape")[2])
                cmds.rename(locator_transform, transform_name)

            # Sensor: gather or create
            sensor_name = self._data["sensorName"]
            new_sensor = None
            # If the sensor was not exported (empty name) don't build it
            if sensor_name:
                new_sensor = cmds.ls(sensor_name, type="AdnSensorRotation")
                if not new_sensor:
                    new_sensor = cmds.createNode("AdnSensorRotation", name=sensor_name)
                else:
                    new_sensor = new_sensor[0]

            self.update()

    def update(self):
        super().update()
        if self.getHost() == AdnHost.kMaya:
            start_node = self._data["sensorStart"]
            mid_node = self._data["sensorMid"]
            end_node = self._data["sensorEnd"]
            locator_name = self._data["name"]
            sensor_name = self._data["sensorName"]

            # Locator and sensor: update start matrix
            self.updateMatrixInput(start_node, locator_name, sensor_name, "startMatrix")
            # Locator and sensor: update mid matrix
            self.updateMatrixInput(mid_node, locator_name, sensor_name, "midMatrix")
            # Locator and sensor: update end matrix
            self.updateMatrixInput(end_node, locator_name, sensor_name, "endMatrix")

            # Locator: draw attributes
            cmds.setAttr("{0}.scale".format(locator_name), self._data["scale"])
            cmds.setAttr("{0}.drawOutput".format(locator_name), self._data["drawOutput"])

            if sensor_name:
                # Sensor: time attributes
                cmds.setAttr("{0}.startTime".format(sensor_name), self._data["startTime"])
                connect_attr("time1.outTime", "{0}.currentTime".format(sensor_name), force=True)
                # Sensor: scale attributes
                cmds.setAttr("{0}.timeScale".format(sensor_name), self._data["timeScale"])

                # Sensor: connect sensor to locator
                connect_attr("{0}.outAngleRemap".format(sensor_name),
                             "{0}.activationAngle".format(locator_name), force=True)
                connect_attr("{0}.outVelocityRemap".format(sensor_name),
                             "{0}.activationVelocity".format(locator_name), force=True)
                connect_attr("{0}.outAccelerationRemap".format(sensor_name),
                             "{0}.activationAcceleration".format(locator_name), force=True)

                # Remappers: min/max ranges
                attributes_map = {
                    "accel": "Acceleration",
                    "vel": "Velocity",
                    "angle": "Angle"
                }
                for key in attributes_map.keys():
                    cmds.setAttr("{0}.inputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMin".format(key)])
                    cmds.setAttr("{0}.inputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeInputMax".format(key)])
                    cmds.setAttr("{0}.outputMin{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMin".format(key)])
                    cmds.setAttr("{0}.outputMax{1}".format(sensor_name, attributes_map[key]),
                                 self._data["{0}RangeOutputMax".format(key)])

            self._failed_connections = self.getRig().setConnections(self._data["connections"])

    def setParameter(self, parameter, value, silent=False):
        result = super().setParameter(parameter, value)
        if result:
            return result
        else:
            try:
                self._data[parameter] = value
            except:
                if not silent:
                    logging.warning("Parameter {0} could not be set as it is not "
                                    "compatible with the sensor.".format(parameter))
                return False
            return True


class AdnActivation(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "name": None,
            "node": None,
            "type": AdnTypes.kActivation,
            "nodes": [],
            "connections": [],
            "inputsIndices": [],
            "inputsBypass": [],
            "inputsValue": [],
            "inputsOperator": [],
            "minOutValue": 0.0,
            "maxOutValue": 1.0
        }
        self._failed_connections = []
        if self not in rig.getUtils():
            rig.addUtil(self)

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        self._data[parameter] = value

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        self.setNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Range
            output_min = cmds.getAttr("{0}.minOutValue".format(node))
            output_max = cmds.getAttr("{0}.maxOutValue".format(node))
            self.setParameter("minOutValue", output_min)
            self.setParameter("maxOutValue", output_max)
            # Inputs
            inputs_index_list = []
            inputs_bypass_list = []
            inputs_value_list = []
            inputs_operator_list = []
            indices = cmds.getAttr("{0}.inputs".format(node), multiIndices=True) or []
            for logical_index in indices:
                child_plug_name = "{0}.inputs[{1}]".format(node, logical_index)
                inputs_index_list.append(logical_index)
                inputs_bypass_list.append(cmds.getAttr("{0}.bypassOperator".format(child_plug_name)))
                inputs_operator_list.append(cmds.getAttr("{0}.operator".format(child_plug_name)))
                inputs_value_list.append(cmds.getAttr("{0}.value".format(child_plug_name)))
            self.setParameter("inputsIndices", inputs_index_list)
            self.setParameter("inputsBypass", inputs_bypass_list)
            self.setParameter("inputsValue", inputs_value_list)
            self.setParameter("inputsOperator", inputs_operator_list)
            # Connections
            self._data["connections"] = self.getRig().getConnections(node)

    def build(self):
        name = self.getName()
        node = None
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(name, type="AdnActivation")
            node = node[0] if node else cmds.createNode("AdnActivation", name=name)
        if node:
            self.setParameter("node", node)
            self.update()

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True, destination=False, plugs=True, connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}".format(source, destination))

    def update(self):
        self.preUpdate()
        node = self._data["node"]
        minOutValue = self._data["minOutValue"]
        maxOutValue = self._data["maxOutValue"]
        inputs_indices = self.resolveIndices()
        inputs_bypass = self._data["inputsBypass"]
        inputs_value = self._data["inputsValue"]
        inputs_operator = self._data["inputsOperator"]
        parameter_connections = self._data["connections"]
        if self.getHost() == AdnHost.kMaya:
            # Range
            cmds.setAttr("{0}.minOutValue".format(node), minOutValue)
            cmds.setAttr("{0}.maxOutValue".format(node), maxOutValue)
            # Inputs
            # Clear compound array attribute to avoid inconsistencies
            inputs_plug = "{0}.inputs".format(node)
            indices = cmds.getAttr(inputs_plug, multiIndices=True) or []
            for logical_index in indices:
                elem_full_name = "{0}[{1}]".format(inputs_plug, logical_index)
                if cmds.objExists(elem_full_name):
                    cmds.removeMultiInstance(elem_full_name, b=True)
            # Recreate the compound array attribute from data
            for elem in range(len(inputs_indices)):
                logical_index = inputs_indices[elem]
                bypass = inputs_bypass[elem]
                operator = inputs_operator[elem]
                value = inputs_value[elem]
                elem_full_name = "{0}[{1}]".format(inputs_plug, logical_index)
                # Set raw values only (connections are handled in `setConnections``)
                cmds.setAttr("{0}.bypassOperator".format(elem_full_name), bypass)
                cmds.setAttr("{0}.operator".format(elem_full_name), operator)
                cmds.setAttr("{0}.value".format(elem_full_name), value)
            # Connections
            self._failed_connections = self.getRig().setConnections(parameter_connections)

    def getFailedConnections(self):
        return self._failed_connections

    def resolveIndices(self):
        indices_list = []
        
        if self.getHost() == AdnHost.kMaya:
            # If indices are present in data, use them, they are logical indices
            if self._data["inputsIndices"]:
                indices_list = self._data["inputsIndices"]
            # If no indices present in data and no connections, then the list of 
            # indices is a range based on the length of the list of values
            elif not self._data["connections"]:
                indices_list = list(range(len(self._data["inputsValue"])))
            # If there are connections, then attempt to extract the logical indices
            # from the input connections
            else:
                node = self._data["node"]
                inputs_index = 0                
                for connection in self._data["connections"]:
                    _, destination = connection
                    inputs_plug = "{0}.inputs".format(node)
                    if inputs_plug not in destination:
                        continue
                    # Extract the index of a given connection to the inputs plug
                    # E.g. "AdnActivation1.inputs[0].value", where match.group(1) = "0"
                    # The parentheses define a capturing group so that match.group(1)
                    # returns the digits found inside the brackets, while match.group(0)
                    # would return the entire matched substring (including the brackets)
                    match = re.search(r'\[(\d+)\]', destination)
                    if not match:
                        continue
                    logical_index = int(match.group(1))
                    indices_list.append(logical_index)
                    inputs_index += 1
        # This should never happen, but ensures that the list of indices is always
        # consistent with the list of values
        if len(indices_list) != len(self._data["inputsValue"]):
            logging.warning("AdnActivation \"{0}\" has {1} indices but {2} values. "
                            "Indices will be set to a range of {3}.".format(self.getName(),
                                                                            len(indices_list),
                                                                            len(self._data["inputsValue"]),
                                                                            len(self._data["inputsValue"])))
            indices_list = list(range(len(self._data["inputsValue"])))
        return indices_list

class AdnLocator(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "type": AdnTypes.kLocatorAdonis,
            "name": None,
            "node": None,
            "userDefinedParameters": [],
            "connections": [],
            "scale": 1.0,
            "transform": {
                "name": None,
                "translate": (0.0, 0.0, 0.0),
                "rotate": (0.0, 0.0, 0.0),
                "scale": (1.0, 1.0, 1.0),
                "userDefinedParameters": [],
                "connections": []
            }
        }
        self._failed_connections = []
        if self not in rig.getSensors():
            rig.addSensor(self)

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        available_parameters = ["name", "type", "transformName",
            "transformTranslate", "transformRotate",
            "transformScale", "scale"]
        if parameter in available_parameters:
            self._data[parameter] = value
            return True
        return False

    def clear(self, force=False):
        if self._rig.getHost() == AdnHost.kMaya:
            for connection in self._connections:
                connection_start = "{0}.{1}".format(connection.start_node,
                                                    connection.start_attribute)
                connection_end = "{0}.{1}".format(connection.end_node,
                                                  connection.end_attribute)
                cmds.disconnectAttr(connection_start, connection_end)
            for node in self._nodes:
                cmds.delete(node)
            cmds.delete(self._node)

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        self.setNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Shape node attributes
            scale = cmds.getAttr("{0}.scale".format(node))
            self.setParameter("scale", scale)
            self.userDefinedParametersFromNode(node,
                                               self._data["userDefinedParameters"])
            # Shape node connections
            self._data["connections"] = self.getRig().getConnections(node)
            # Transform node
            parent = cmds.listRelatives(node, parent=True,
                                        type="transform") or []
            if parent:
                # Transform node attributes
                transform = parent[0]
                self._data["transform"]["name"] = transform
                self._data["transform"]["translate"] = cmds.getAttr("{0}.translate".format(transform))[0]
                self._data["transform"]["rotate"] = cmds.getAttr("{0}.rotate".format(transform))[0]
                self._data["transform"]["scale"] = cmds.getAttr("{0}.scale".format(transform))[0]
                self.userDefinedParametersFromNode(self._data["transform"]["name"],
                                                   self._data["transform"]["userDefinedParameters"])
                # Transform node connections
                self._data["transform"]["connections"] = self.getRig().getConnections(transform)

    def build(self):
        name = self.getName()
        node = None
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(name, type="AdnLocator")
            node = node[0] if node else cmds.createNode("AdnLocator", name=name)
        if node:
            self.setParameter("node", node)
            self.update()

    def update(self):
        self.preUpdate()
        locator_name = self._data["name"]
        # Shape node attributes
        cmds.setAttr("{0}.scale".format(locator_name), self._data["scale"])
        self.updateUserDefinedParameters(locator_name,
                                      self._data["userDefinedParameters"])
        # Transform node attributes
        transform_name = self._data["transform"]["name"]
        if transform_name:
            cmds.setAttr("{0}.translate".format(transform_name),
                         self._data["transform"]["translate"][0],
                         self._data["transform"]["translate"][1],
                         self._data["transform"]["translate"][2],
                         type="double3")
            cmds.setAttr("{0}.rotate".format(transform_name),
                         self._data["transform"]["rotate"][0],
                         self._data["transform"]["rotate"][1],
                         self._data["transform"]["rotate"][2],
                         type="double3")
            cmds.setAttr("{0}.scale".format(transform_name),
                         self._data["transform"]["scale"][0],
                         self._data["transform"]["scale"][1],
                         self._data["transform"]["scale"][2],
                         type="double3")
            self.updateUserDefinedParameters(transform_name,
                                          self._data["transform"]["userDefinedParameters"])
        # Connections (shape node and transform node)
        self._failed_connections = self.getRig().setConnections(self._data["connections"])
        self._failed_connections += self.getRig().setConnections(self._data["transform"]["connections"])

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True,
                                                     destination=False,
                                                     plugs=True,
                                                     connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}"
                                    "".format(source, destination))

    @staticmethod
    def userDefinedParametersFromNode(node, custom_attr_list):
        parameters_list = cmds.listAttr(node, userDefined=True) or []
        for parameter in parameters_list:
            parameter_obj = None
            if not cmds.attributeQuery(parameter, node=node, exists=True):
                continue
            # Gather attribute to create an AdnParameter object
            try:
                value = cmds.getAttr("{0}.{1}".format(node, parameter))
                attribute_type = cmds.attributeQuery(parameter,
                                                     node=node,
                                                     attributeType=True)
                parameter_obj = AdnParameter(parameter, value, attribute_type)
            except Exception as e:
                logging.error("Could not gather parameter value: {0}".format(e))
                continue
            if not parameter_obj:
                continue
            try:
                parameter_obj.min = cmds.attributeQuery(parameter,
                                                        node=node,
                                                        min=True)[0]
                parameter_obj.max = cmds.attributeQuery(parameter,
                                                        node=node,
                                                        max=True)[0]
            except:
                # Querying min/max would fail if the attribute has
                # no min/max defined
                pass

            custom_attr_list.append(parameter_obj.getData())

    @staticmethod
    def updateUserDefinedParameters(node, custom_attr_list):
        for parameter_dict in custom_attr_list:
            attribute = parameter_dict.get("name")
            attr_type = parameter_dict.get("type")
            attr_value = parameter_dict.get("value")
            min_value = parameter_dict.get("min")
            max_value = parameter_dict.get("max")
            if not cmds.attributeQuery(attribute, node=node, exists=True):
                # Build the keyword arguments for addAttr
                kwargs = {"longName": attribute,
                          "attributeType": attr_type}
                # Create the attribute and set value
                cmds.addAttr(node, **kwargs)

            cmds.setAttr("{0}.{1}".format(node, attribute), attr_value)
            # Update min and max values if provided
            edit_kwargs = {}
            if min_value is not None:
                edit_kwargs["min"] = min_value
            if max_value is not None:
                edit_kwargs["max"] = max_value
            if min_value is not None or max_value is not None:
                cmds.addAttr("{0}.{1}".format(node, attribute), edit=True, **edit_kwargs)

    def getFailedConnections(self):
        return self._failed_connections


class AdnEdgeEvaluator(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "name": None,
            "node": None,
            "type": AdnTypes.kEdgeEvaluator,
            "nodes": [],
            "connections": [],
            "initializationTime": 0,
            "restMesh": None,
            "deformMesh": None,
        }
        self._failed_connections = []

    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        self._data[parameter] = value

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setName(node)
        self.setNode(node)
        if self.getHost() == AdnHost.kMaya:
            # Initialization time
            initialization_time = cmds.getAttr("{0}.initializationTime".format(node))
            self.setParameter("initializationTime", initialization_time)

            # Rest mesh
            rest_mesh = cmds.listConnections("{0}.restMesh".format(node)) or []
            rest_mesh = rest_mesh[0] if rest_mesh else None
            self.setParameter("restMesh", rest_mesh)
            # Deform mesh
            deform_mesh = cmds.listConnections("{0}.deformMesh".format(node)) or []
            deform_mesh = deform_mesh[0] if deform_mesh else None
            self.setParameter("deformMesh", deform_mesh)

            # Connections
            ignore_at_destination = ["restMesh", "deformMesh"]
            self._data["connections"] = self.getRig().getConnections(node, ignore_at_destination=ignore_at_destination)

    def build(self):
        name = self.getName()
        node = None
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(name, type="AdnEdgeEvaluator")
            node = node[0] if node else cmds.createNode("AdnEdgeEvaluator", name=name)
        if node:
            self.setParameter("node", node)
            self.update()

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True,
                                                     destination=False,
                                                     plugs=True,
                                                     connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}"
                                    "".format(source, destination))

    def update(self):
        self.preUpdate()
        node = self.getNode()
        name = self.getName()
        if self.getHost() == AdnHost.kMaya:
            # Initialization time
            initialization_time = self._data["initializationTime"]
            cmds.setAttr("{0}.initializationTime".format(node), initialization_time)

            # Rest mesh
            rest_mesh = self._data["restMesh"]
            if rest_mesh:
                connect_attr("{0}.outMesh".format(rest_mesh),
                             "{0}.restMesh".format(node), force=True)

            # Deform mesh
            deform_mesh = self._data["deformMesh"]
            if deform_mesh:
                connect_attr("{0}.outMesh".format(deform_mesh),
                             "{0}.deformMesh".format(node), force=True)

            # Connections
            self._failed_connections = self.getRig().setConnections(self._data["connections"])

    def getFailedConnections(self):
        return self._failed_connections


class AdnRemap(object):
    def __init__(self, rig):
        self._rig = rig
        self._data = {
            "type": AdnTypes.kRemap,
            "input": 0.0,
            "inputMin": 0.0,
            "inputMax": 1.0,
            "outputMin": 0.0,
            "outputMax": 1.0,
            "positions": [],
            "values": [],
            "interpolations": []
        }
        self._failed_connections = []
    
    def reset(self):
        rig = self.getRig()
        self.__init__(rig)

    def getHost(self):
        return self.getRig().getHost()

    def setName(self, name):
        self._data["name"] = name

    def getName(self):
        return self._data["name"]

    def setRig(self, rig):
        self._rig = rig

    def getRig(self):
        return self._rig

    def setNode(self, node):
        self._data["node"] = node

    def getNode(self):
        return self._data["node"]

    def setParameter(self, parameter, value):
        self._data[parameter] = value

    def getData(self):
        return self._data

    def fromDict(self, in_dictionary):
        self.reset()
        set_parameters = []
        for parameter in in_dictionary.keys():
            result = self.setParameter(parameter, in_dictionary[parameter])
            if result:
                set_parameters.append(parameter)
        return set_parameters

    def fromNode(self, node):
        self._failed_connections = []
        self.setNode(node)
        self.setName(node)
        if self.getHost() == AdnHost.kMaya:
            # Scalar parameters
            self.setParameter("input", cmds.getAttr("{0}.input".format(node)))
            self.setParameter("inputMin", cmds.getAttr("{0}.inputMin".format(node)))
            self.setParameter("inputMax", cmds.getAttr("{0}.inputMax".format(node)))
            self.setParameter("outputMin", cmds.getAttr("{0}.outputMin".format(node)))
            self.setParameter("outputMax", cmds.getAttr("{0}.outputMax".format(node)))
            
            # Ramp
            remap_indices = cmds.getAttr("{0}.remap".format(node), multiIndices=True) or []
            positions = []
            values = []
            interpolations = []
            for i in remap_indices:
                positions.append(cmds.getAttr("{0}.remap[{1}].remap_Position".format(node, i)))
                values.append(cmds.getAttr("{0}.remap[{1}].remap_FloatValue".format(node, i)))
                interpolation = cmds.getAttr("{0}.remap[{1}].remap_Interp".format(node, i))
                interpolations.append(MAYA_TO_ADN_RAMP_INTERP_MODE[interpolation])
            self.setParameter("positions", positions)
            self.setParameter("values", values)
            self.setParameter("interpolations", interpolations)
            
            # Connections
            self._data["connections"] = self.getRig().getConnections(node)

    def build(self):
        name = self.getName()
        node = None
        if self.getHost() == AdnHost.kMaya:
            node = cmds.ls(name, type="AdnRemap")
            node = node[0] if node else cmds.createNode("AdnRemap", name=name)
        if node:
            self.setParameter("node", node)
            self.update()

    def preUpdate(self):
        if self.getHost() == AdnHost.kMaya:
            node = self.getNode()
            input_connections = cmds.listConnections(node, source=True,
                                                     destination=False,
                                                     plugs=True,
                                                     connections=True) or []
            for i in range(len(input_connections) // 2):
                destination = input_connections[i * 2]
                source = input_connections[i * 2 + 1]
                try:
                    cmds.disconnectAttr(source, destination)
                except:
                    logging.warning("Could not disconnect {0} from {1}"
                                    "".format(source, destination))

    def update(self):
        self.preUpdate()
        node = self.getNode()
        if self.getHost() == AdnHost.kMaya:
            # Scalar parameters
            cmds.setAttr("{0}.input".format(node), self._data["input"])
            cmds.setAttr("{0}.inputMin".format(node), self._data["inputMin"])
            cmds.setAttr("{0}.inputMax".format(node), self._data["inputMax"])
            cmds.setAttr("{0}.outputMin".format(node), self._data["outputMin"])
            cmds.setAttr("{0}.outputMax".format(node), self._data["outputMax"])
            
            # Ramp
            # Clear the existing ramp values (if any)
            existing = cmds.getAttr("{0}.remap".format(node), multiIndices=True) or []
            for i in existing:
                cmds.removeMultiInstance("{0}.remap[{1}]".format(node, i), b=True)
            # Set the new ramp values
            positions = self._data["positions"]
            values = self._data["values"]
            interpolations = self._data["interpolations"]
            size = len(positions)
            for i in range(size):
                cmds.setAttr("{0}.remap[{1}].remap_Position".format(node, i), positions[i])
                cmds.setAttr("{0}.remap[{1}].remap_FloatValue".format(node, i), values[i])
                interpolation = ADN_TO_MAYA_RAMP_INTERP_MODE[interpolations[i]]
                cmds.setAttr("{0}.remap[{1}].remap_Interp".format(node, i), interpolation)

            # Connections
            self._failed_connections = self.getRig().setConnections(self._data["connections"])

    def getFailedConnections(self):
        return self._failed_connections
