import os
import json
import logging

import maya.cmds as cmds

from adn.tools.maya.attribute_handlers import disconnect_nodes
from adn.utils.constants import DeformerTypes, LocatorTypes, OtherNodeTypes, SensorTypes
from adn.utils.maya.constants import IOFeaturesData
from adn.utils.maya.checkers import check_connections_exist


def gather_from_scene(enabled_features=None):
    """Gather the scene data and encapsulate it in and AdonisFX
    API rig instance.

    Args:
        enabled_features (dict, optional): A dictionary where keys are feature
            names and values are flags to determine if a feature has to be
            gathered or bypassed. If this is not provided, all features will be
            gathered. Defaults to None.

    Returns:
        dict: dictionary containing the rig scene data.
    """
    data = {
        IOFeaturesData.SENSOR: list(),
        IOFeaturesData.ACTIVATION: list(),
        IOFeaturesData.MUSCLE: list(),
        IOFeaturesData.GLUE: list(),
        IOFeaturesData.SKIN: list(),
        IOFeaturesData.FAT: list(),
        IOFeaturesData.RELAX: list(),
        IOFeaturesData.SKIN_MERGE: list(),
        IOFeaturesData.SIMSHAPE: list(),
        IOFeaturesData.EDGE_EVALUATOR: list(),
        IOFeaturesData.REMAP: list()
    }

    # Gather all features by default if `enabled_features` is not provided
    feature_names = data.keys()
    gather_flags = {
        feature: enabled_features.get(feature, True) if enabled_features else True
        for feature in feature_names
    }

    # Create the Adonis rig instance
    from adn.api import adnx
    rig = adnx.AdnRig(adnx.AdnHost.kMaya)

    # Sensors and locators
    if gather_flags[IOFeaturesData.SENSOR]:
        for node in cmds.ls(type=[LocatorTypes.DISTANCE]):
            sensor = adnx.AdnSensorDistance(rig)
            sensor.fromNode(node)
            data[IOFeaturesData.SENSOR].append(sensor._data)

        for node in cmds.ls(type=[LocatorTypes.POSITION]):
            sensor = adnx.AdnSensorPosition(rig)
            sensor.fromNode(node)
            data[IOFeaturesData.SENSOR].append(sensor._data)

        for node in cmds.ls(type=[LocatorTypes.ROTATION]):
            sensor = adnx.AdnSensorRotation(rig)
            sensor.fromNode(node)
            data[IOFeaturesData.SENSOR].append(sensor._data)

        for node in cmds.ls(type=[LocatorTypes.DEFAULT]):
            locator = adnx.AdnLocator(rig)
            locator.fromNode(node)
            data[IOFeaturesData.SENSOR].append(locator._data)

    # Activation
    if gather_flags[IOFeaturesData.ACTIVATION]:
        activation_list = cmds.ls(type=OtherNodeTypes.ACTIVATION)
        for node in activation_list:
            activation = adnx.AdnActivation(rig)
            activation.fromNode(node)
            data[IOFeaturesData.ACTIVATION].append(activation._data)

    # Remap
    if gather_flags[IOFeaturesData.REMAP]:
        remap_list = cmds.ls(type=OtherNodeTypes.REMAP)
        for node in remap_list:
            remap = adnx.AdnRemap(rig)
            remap.fromNode(node)
            data[IOFeaturesData.REMAP].append(remap._data)

    # Muscles
    if gather_flags[IOFeaturesData.MUSCLE]:
        muscle_list = cmds.ls(type=DeformerTypes.MUSCLE)
        for node in muscle_list:
            muscle = adnx.AdnMuscle(rig)
            muscle.fromNode(node)
            data[IOFeaturesData.MUSCLE].append(muscle._data)
        ribbon_list = cmds.ls(type=DeformerTypes.RIBBON)
        for node in ribbon_list:
            ribbon = adnx.AdnRibbonMuscle(rig)
            ribbon.fromNode(node)
            data[IOFeaturesData.MUSCLE].append(ribbon._data)

    # Glue
    if gather_flags[IOFeaturesData.GLUE]:
        glue_list = cmds.ls(type=OtherNodeTypes.GLUE)
        for node in glue_list:
            glue = adnx.AdnGlue(rig)
            glue.fromNode(node)
            data[IOFeaturesData.GLUE].append(glue._data)

    # Skin
    if gather_flags[IOFeaturesData.SKIN]:
        skin_list = cmds.ls(type=DeformerTypes.SKIN)
        for node in skin_list:
            skin = adnx.AdnSkin(rig)
            skin.fromNode(node)
            data[IOFeaturesData.SKIN].append(skin._data)

    # Fat
    if gather_flags[IOFeaturesData.FAT]:
        fat_list = cmds.ls(type=DeformerTypes.FAT)
        for node in fat_list:
            fat = adnx.AdnFat(rig)
            fat.fromNode(node)
            data[IOFeaturesData.FAT].append(fat._data)

    # Relax
    if gather_flags[IOFeaturesData.RELAX]:
        relax_list = cmds.ls(type=DeformerTypes.RELAX)
        for node in relax_list:
            relax = adnx.AdnRelax(rig)
            relax.fromNode(node)
            data[IOFeaturesData.RELAX].append(relax._data)

    # Skin Merge
    if gather_flags[IOFeaturesData.SKIN_MERGE]:
        skin_merge_list = cmds.ls(type=DeformerTypes.SKIN_MERGE)
        for node in skin_merge_list:
            skin_merge = adnx.AdnSkinMerge(rig)
            skin_merge.fromNode(node)
            data[IOFeaturesData.SKIN_MERGE].append(skin_merge._data)

    # Simshape
    if gather_flags[IOFeaturesData.SIMSHAPE]:
        simshape_list = cmds.ls(type=DeformerTypes.SIMSHAPE)
        for node in simshape_list:
            simshape = adnx.AdnSimshape(rig)
            simshape.fromNode(node)
            data[IOFeaturesData.SIMSHAPE].append(simshape._data)

    # Edge Evaluator
    if gather_flags[IOFeaturesData.EDGE_EVALUATOR]:
        edge_evaluator_list = cmds.ls(type=OtherNodeTypes.EDGE_EVALUATOR)
        for node in edge_evaluator_list:
            edge_evaluator = adnx.AdnEdgeEvaluator(rig)
            edge_evaluator.fromNode(node)
            data[IOFeaturesData.EDGE_EVALUATOR].append(edge_evaluator._data)

    return data


def clear_scene():
    """Clear all AdonisFX related data from the scene.
    """
    # Remove activations
    activation_list = cmds.ls(type=OtherNodeTypes.ACTIVATION)
    if activation_list:
        disconnect_nodes(activation_list)
        cmds.delete(activation_list)

    # Remove remap nodes
    remap_list = cmds.ls(type=OtherNodeTypes.REMAP)
    if remap_list:
        disconnect_nodes(remap_list)
        cmds.delete(remap_list)

    # Remove sensors
    sensor_list = cmds.ls(type=[SensorTypes.DISTANCE,
                                SensorTypes.POSITION,
                                SensorTypes.ROTATION])
    if sensor_list:
        for sensor_node in sensor_list:
            sensor_remaps = cmds.listConnections(sensor_node, source=False,
                                                 destination=True, type="remapValue") or []
            for remap_node in sensor_remaps:
                cmds.delete(remap_node)
        sensor_list = cmds.ls(type=[SensorTypes.DISTANCE,
                                    SensorTypes.POSITION,
                                    SensorTypes.ROTATION])
        if sensor_list:
            disconnect_nodes(sensor_list)
            cmds.delete(sensor_list)

    # Remove locators
    locator_list = cmds.ls(type=[LocatorTypes.DEFAULT, LocatorTypes.DISTANCE,
                                 LocatorTypes.POSITION, LocatorTypes.ROTATION])
    if locator_list:
        disconnect_nodes(locator_list)
        locator_transforms = cmds.listRelatives(locator_list, parent=True) or []
        disconnect_nodes(locator_transforms)
        cmds.delete(locator_transforms + locator_list)

    # Remove muscles
    muscle_list = cmds.ls(type=[DeformerTypes.MUSCLE, DeformerTypes.RIBBON])
    if muscle_list:
        disconnect_nodes(muscle_list)
        cmds.delete(muscle_list)

    # Remove glue
    glue_list = cmds.ls(type=OtherNodeTypes.GLUE)
    if glue_list:
        disconnect_nodes(glue_list)
        cmds.delete(glue_list)

    # Remove skin
    skin_list = cmds.ls(type=DeformerTypes.SKIN)
    if skin_list:
        disconnect_nodes(skin_list)
        cmds.delete(skin_list)

    # Remove fat
    fat_list = cmds.ls(type=DeformerTypes.FAT)
    if fat_list:
        disconnect_nodes(fat_list)
        cmds.delete(fat_list)

    # Remove relax
    relax_list = cmds.ls(type=DeformerTypes.RELAX)
    if relax_list:
        disconnect_nodes(relax_list)
        cmds.delete(relax_list)

    # Remove skin merge
    skin_merge_list = cmds.ls(type=DeformerTypes.SKIN_MERGE)
    if skin_merge_list:
        disconnect_nodes(skin_merge_list)
        cmds.delete(skin_merge_list)

    # Remove simshape
    simshape_list = cmds.ls(type=DeformerTypes.SIMSHAPE)
    if simshape_list:
        disconnect_nodes(simshape_list)
        cmds.delete(simshape_list)

    # Remove AdnDebugLocator
    adn_debug_locator_list = cmds.ls(type="AdnDebugLocator")
    if adn_debug_locator_list:
        disconnect_nodes(adn_debug_locator_list)
        adn_debug_locator_transforms = cmds.listRelatives(adn_debug_locator_list, parent=True) or []
        disconnect_nodes(adn_debug_locator_transforms)
        cmds.delete(adn_debug_locator_list + adn_debug_locator_transforms)

    # Remove AdnDataNode
    adn_data_node_list = cmds.ls(type="AdnDataNode")
    if adn_data_node_list:
        disconnect_nodes(adn_data_node_list)
        cmds.delete(adn_data_node_list)

    # Remove AdnEdgeEvaluator
    edge_evaluator_list = cmds.ls(type=OtherNodeTypes.EDGE_EVALUATOR)
    if edge_evaluator_list:
        disconnect_nodes(edge_evaluator_list)
        cmds.delete(edge_evaluator_list)


def build_from_data(in_data, enabled_features=None):
    """Rebuild the AdonisFX rig data.

    Args:
        in_data (dict): AdonisFX dictionary with the mapped data.
        enabled_features (dict, optional): A dictionary where keys are feature
            names and values are flags to determine if a feature has to be
            built or bypassed. If this is not provided, all features will be
            built. Defaults to None.
    """
    if not in_data:
        return

    # Build all features by default if `enabled_features` is not provided
    feature_names = [
        IOFeaturesData.SENSOR,
        IOFeaturesData.ACTIVATION,
        IOFeaturesData.MUSCLE,
        IOFeaturesData.GLUE,
        IOFeaturesData.SKIN,
        IOFeaturesData.FAT,
        IOFeaturesData.RELAX,
        IOFeaturesData.SKIN_MERGE,
        IOFeaturesData.SIMSHAPE,
        IOFeaturesData.EDGE_EVALUATOR,
        IOFeaturesData.REMAP
    ]

    build_flags = {
        feature: enabled_features.get(feature, True) if enabled_features else True
        for feature in feature_names
    }

    # Create the Adonis rig instance
    from adn.api import adnx
    rig = adnx.AdnRig(adnx.AdnHost.kMaya)

    failed_connections = {}

    # Build sensors and locators
    if build_flags[IOFeaturesData.SENSOR] and IOFeaturesData.SENSOR in in_data:
        for data in in_data[IOFeaturesData.SENSOR]:
            if "type" not in data:
                continue
            sensor = None
            if data["type"] == adnx.AdnTypes.kSensorDistance:
                sensor = adnx.AdnSensorDistance(rig)
            elif data["type"] == adnx.AdnTypes.kSensorPosition:
                sensor = adnx.AdnSensorPosition(rig)
            elif data["type"] == adnx.AdnTypes.kSensorAngle:
                sensor = adnx.AdnSensorRotation(rig)
            elif data["type"] == adnx.AdnTypes.kLocatorAdonis:
                sensor = adnx.AdnLocator(rig)
            else:
                continue
            sensor.fromDict(data)
            sensor.build()
            failed_connections[sensor.getName()] = sensor.getFailedConnections()

    # Rebuild activations
    if build_flags[IOFeaturesData.ACTIVATION] and IOFeaturesData.ACTIVATION in in_data:
        for data in in_data[IOFeaturesData.ACTIVATION]:
            activation = adnx.AdnActivation(rig)
            activation.fromDict(data)
            activation.build()
            failed_connections[activation.getName()] = activation.getFailedConnections()

    # Rebuild remaps
    if build_flags[IOFeaturesData.REMAP] and IOFeaturesData.REMAP in in_data:
        for data in in_data[IOFeaturesData.REMAP]:
            remap = adnx.AdnRemap(rig)
            remap.fromDict(data)
            remap.build()
            failed_connections[remap.getName()] = remap.getFailedConnections()

    # Rebuild the muscles
    if build_flags[IOFeaturesData.MUSCLE] and IOFeaturesData.MUSCLE in in_data:
        for data in in_data[IOFeaturesData.MUSCLE]:
            muscle = None
            if data["type"] == adnx.AdnTypes.kMuscle:
                muscle = adnx.AdnMuscle(rig)
            elif data["type"] == adnx.AdnTypes.kRibbon:
                muscle = adnx.AdnRibbonMuscle(rig)
            else:
                continue
            muscle.fromDict(data)
            muscle.build()
            failed_connections[muscle.getName()] = muscle.getFailedConnections()

    # Rebuild the glues
    if build_flags[IOFeaturesData.GLUE] and IOFeaturesData.GLUE in in_data:
        for data in in_data[IOFeaturesData.GLUE]:
            glue = adnx.AdnGlue(rig)
            glue.fromDict(data)
            glue.build()
            failed_connections[glue.getName()] = glue.getFailedConnections()

    # Rebuild the skins
    if build_flags[IOFeaturesData.SKIN] and IOFeaturesData.SKIN in in_data:
        for data in in_data[IOFeaturesData.SKIN]:
            skin = adnx.AdnSkin(rig)
            skin.fromDict(data)
            skin.build()
            failed_connections[skin.getName()] = skin.getFailedConnections()

    # Rebuild the fats
    if build_flags[IOFeaturesData.FAT] and IOFeaturesData.FAT in in_data:
        for data in in_data[IOFeaturesData.FAT]:
            fat = adnx.AdnFat(rig)
            fat.fromDict(data)
            fat.build()
            failed_connections[fat.getName()] = fat.getFailedConnections()

    # Rebuild the relax nodes
    if build_flags[IOFeaturesData.RELAX] and IOFeaturesData.RELAX in in_data:
        for data in in_data[IOFeaturesData.RELAX]:
            relax = adnx.AdnRelax(rig)
            relax.fromDict(data)
            relax.build()
            failed_connections[relax.getName()] = relax.getFailedConnections()
    
    # Rebuild the skin merge nodes
    if build_flags[IOFeaturesData.SKIN_MERGE] and IOFeaturesData.SKIN_MERGE in in_data:
        for data in in_data[IOFeaturesData.SKIN_MERGE]:
            skin_merge = adnx.AdnSkinMerge(rig)
            skin_merge.fromDict(data)
            skin_merge.build()
            failed_connections[skin_merge.getName()] = skin_merge.getFailedConnections()

    # Rebuild the simshape nodes
    if build_flags[IOFeaturesData.SIMSHAPE] and IOFeaturesData.SIMSHAPE in in_data:
        for data in in_data[IOFeaturesData.SIMSHAPE]:
            simshape = adnx.AdnSimshape(rig)
            simshape.fromDict(data)
            simshape.build()
            failed_connections[simshape.getName()] = simshape.getFailedConnections()

    # Rebuild the edge evaluator nodes
    if build_flags[IOFeaturesData.EDGE_EVALUATOR] and IOFeaturesData.EDGE_EVALUATOR in in_data:
        for data in in_data[IOFeaturesData.EDGE_EVALUATOR]:
            edge_evaluator = adnx.AdnEdgeEvaluator(rig)
            edge_evaluator.fromDict(data)
            edge_evaluator.build()
            failed_connections[edge_evaluator.getName()] = edge_evaluator.getFailedConnections()

    # Print warnings with the connections that could not be made
    for node, connections in check_connections_exist(failed_connections).items():
        logging.warning("{0}: Failed connections: {1}".format(node, connections))


def import_data(file_path, enabled_features=None):
    """Imports the AdonisFX setup from the given JSON file into the scene.

    This function reads the AdonisFX setup from a specified JSON file and imports
    it into the current scene. The imported data can include different features
    such as sensor, activation, muscle, glue, skin, fat, and relax nodes.

    These features will be imported if their corresponding flag in the
    `enabled_features` dictionary is set to True. If `enabled_features` is not
    provided, all features will be imported by default.

    Args:
        file_path (str): Path to the JSON file with the AdonisFX setup.
        enabled_features (dict, optional): A dictionary where keys are feature
            names and values are flags to determine if a feature has to be
            imported or not. If this is not provided, all features will be
            imported. Defaults to None.

    Returns:
        bool: True if the data was successfully imported, False otherwise.
    """
    if not os.path.exists(file_path):
        logging.error("File not found: {0}".format(file_path))
        return False

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        logging.error("Failed to read or parse the file: {0}. Error: {1}".format(file_path, e))
        return False

    build_from_data(data, enabled_features)
    return True


def export_data(file_path, enabled_features=None):
    """Export the AdonisFX setup from the scene to a JSON file.

    This function gathers the current AdonisFX setup from the scene and exports
    it to a specified JSON file. The exported data can include different features
    such as sensor, activation, muscle, glue, skin, fat, and relax nodes.

    These features will be exported if their corresponding flag in the
    `enabled_features` dictionary is set to True. If `enabled_features` is not
    provided, all features will be exported by default.

    Args:
        file_path (str): Path to the JSON file with the AdonisFX setup.
        enabled_features (dict, optional): A dictionary where keys are feature
            names and values are flags to determine if a feature has to be
            exported or not. If this is not provided, all features will be
            exported. Defaults to None.

    Returns:
        bool: True if the data was successfully exported, False otherwise.
    """
    data = gather_from_scene(enabled_features)
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except (IOError, json.JSONDecodeError) as e:
        logging.error("Failed to write into the file: {0}. Error: {1}".format(file_path, e))
        return False

    return True
