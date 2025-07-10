import maya.cmds as cmds

from adn.utils.constants import UiConstants, DeformerTypes, StatusCode
from adn.utils.maya.checkers import check_playback
from adn.ui.utils import cursor
from adn.tools.maya import locators
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check


def apply_deformer(destination_mesh, anim_mesh=None, deform_mesh=None,
                   rest_mesh=None, muscles_data=None, custom_name=None):
    """Create the simshape deformer and generate any necessary connections
    between nodes.

    Args:
        destination_mesh (str): Destination mesh to which AdnSimshape will be
            applied to.
        anim_mesh (str, optional): Input animated mesh plugged into the
            AdnSimshape deformer. Defaults to None.
        deform_mesh (str, optional): Input deformed mesh plugged into the
            AdnSimshape deformer. Defaults to None.
        rest_mesh (str, optional): Input rest mesh plugged into the
            AdnSimshape deformer. Defaults to None.
        muscles_data (str, optional): Muscles data file path.
            Defaults to None.
        custom_name (str, optional): Custom name to give to the deformer.
            Defaults to None.

    Returns:
        str: Name of the created AdnSimshape deformer.
    """
    simshape_node = (cmds.deformer(destination_mesh, type=DeformerTypes.SIMSHAPE)[0] if not custom_name
                     else cmds.deformer(destination_mesh, type=DeformerTypes.SIMSHAPE, name=custom_name)[0])
    if rest_mesh:
        cmds.connectAttr("{0}.outMesh".format(rest_mesh),
                         "{0}.restMesh".format(simshape_node))
    if anim_mesh:
        cmds.connectAttr("{0}.outMesh".format(anim_mesh),
                         "{0}.animMesh".format(simshape_node))
    if deform_mesh:
        cmds.connectAttr("{0}.outMesh".format(deform_mesh),
                         "{0}.deformMesh".format(simshape_node))
        if muscles_data:
            cmds.setAttr("{0}.musclesFile".format(simshape_node), muscles_data, type="string")
    cmds.setAttr("{0}.prerollStartTime".format(simshape_node), cmds.currentTime(query=True))
    cmds.setAttr("{0}.startTime".format(simshape_node), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(simshape_node))
    cmds.setAttr("{0}.material".format(simshape_node), 7)

    return simshape_node


def create_default_simshape(mesh_name, node_name):
    """Create the most basic simshape deformer. Only time attributes are
    configured for security reasons.

    Args:
        mesh_name (str): name of the geometry to create the deformer onto.
        node_name (str): tentative name for the node to create.

    Returns:
        str: resulting name of the created node.
        bool: False if there was an error. True otherwise.
    """
    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        # Deformer and connections
        deformer = cmds.deformer(mesh_name,
                                 type=DeformerTypes.SIMSHAPE,
                                 name=node_name)[0]
        cmds.setAttr("{0}.prerollStartTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.connectAttr("time1.outTime",
                         "{0}.currentTime".format(deformer))

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

    return deformer, connect_to_debugger_success


def check_selection(selection):
    """Check if the selection contains 1 or 2 objects and if the destination
    mesh already contains a AdnSimshape deformer.

    Args:
        selection (list): Selection list contained the currently selected objects.

    Returns:
        :obj:`StatusCode`: If the selection is empty or contains more than 2 objects (ERROR).
            If the selection is correct but an AdnSimshape deformer is already applied (WARNING).
            Fully success (SUCCESS).
    """
    if not selection or len(selection) > 2:
        print("{0} Wrong number of meshes selected ({1}). "
              "Please, select in the following order: "
              "1) [optional] rest mesh to initialize points data, "
              "2) mesh to apply the simulation to."
              "".format(UiConstants.ERROR_PREFIX, len(selection)))
        return StatusCode.ERROR

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.SIMSHAPE:
            print("{0} The selected mesh ({1}) has already an AdnSimshape deformer node "
                  "applied to. Aborting creation."
                  "".format(UiConstants.WARNING_PREFIX, short_name[0]))
            return StatusCode.WARNING

    return StatusCode.SUCCESS


@undo_chunk
def apply_simshape(custom_name=None):
    """Apply AdnSimshape with the desired checks for correct creation.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.

    Returns:
        str: deformer name.
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    simshape_node_name = ""
    connect_to_debugger_success = True
    cmds.filterExpand(selectionMask=12, fullPath=True)
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh",
                        long=True, noIntermediate=True)
    check_result = check_selection(selection)
    if check_result == StatusCode.SUCCESS:
        destination_shape = selection[-1]
        rest_shape = selection[-2] if len(selection) == 2 else None

        # Number of vertices check
        if rest_shape:
            num_vertices_rest_mesh = cmds.polyEvaluate(rest_shape, vertex=True)
            num_vertices_sim_mesh = cmds.polyEvaluate(destination_shape, vertex=True)
            if num_vertices_rest_mesh != num_vertices_sim_mesh:
                print("{0} Selected meshes have different vertex count. Please, make "
                      "sure to select two compatible meshes and try again."
                      "".format(UiConstants.ERROR_PREFIX))
                return simshape_node_name, False

        with cursor.wait_cursor_context():
            simshape_node_name = apply_deformer(destination_shape,
                                                rest_mesh=rest_shape,
                                                custom_name=custom_name)
        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(simshape_node_name)
        # Restore selection
        cmds.select(selection)
        # Creation dialog
        simshape_short_name = cmds.ls(simshape_node_name, shortNames=True)[0]
        print("{0} \"{1}\" deformer has been created successfully."
              "".format(UiConstants.INFO_PREFIX, simshape_short_name))
    elif check_result == StatusCode.ERROR:
        return simshape_node_name, False

    return simshape_node_name, connect_to_debugger_success


def get_simshape_deformer(obj):
    """Retrieves a simshape deformer node connected to the given object.

    Args:
        obj (str): object to retrieve a simshape deformer from.

    Returns:
        str: name of the simshape deformer if found (None otherwise).
    """
    history = cmds.listHistory(obj)
    simshape_nodes = [node for node in history if
                      cmds.nodeType(node) == DeformerTypes.SIMSHAPE]
    if not simshape_nodes:
        return None
    return simshape_nodes[0]


@undo_chunk
def add_mesh(mesh_plug, force=True):
    """Connects a given mesh to one of the mesh plugs of simshape.
    The destination plug is specified by the input argument. The source mesh
    and the destination simshape deformer are retrieved from the current
    selection in that order.

    Args:
        mesh_plug (str): short name to identify the plug to make the
            connection to (i.e. rest, deform or anim).
        force (bool, optional): If the mesh plug has to be overridden. Defaults to True.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()

    current_selection = cmds.ls(selection=True, long=True)
    if len(current_selection) < 2:
        print("{0} Invalid selection to add a {1} mesh to simshape. Please, "
              "select first the mesh to connect and then the simshape "
              "mesh.".format(UiConstants.ERROR_PREFIX, mesh_plug))
        return False
    input_mesh = current_selection[-2]
    simshape_node = get_simshape_deformer(current_selection[-1])
    if not simshape_node:
        selection_short_name = cmds.ls(current_selection[-1], shortNames=True)[0]
        print("{0} Could not find a valid AdnSimshape deformer assigned to "
              "\"{1}\".".format(UiConstants.ERROR_PREFIX, selection_short_name))
        return False

    # Number vertices check
    num_vertices_input_mesh = cmds.polyEvaluate(input_mesh, vertex=True)
    num_vertices_sim_mesh = cmds.polyEvaluate(current_selection[-1], vertex=True)
    if num_vertices_input_mesh != num_vertices_sim_mesh:
        print("{0} Selected meshes have different vertex count. Please, make sure "
              "to select two compatible meshes and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    try:
        cmds.connectAttr("{0}.outMesh".format(input_mesh),
                        "{0}.{1}Mesh".format(simshape_node, mesh_plug),
                        force=force)
    except:
        print("{0} Could not add the {1} mesh because there is already a mesh connected."
              "".format(UiConstants.ERROR_PREFIX, mesh_plug))
        return False

    mesh_short_name = cmds.ls(input_mesh, shortNames=True)[0]
    simshape_short_name = cmds.ls(simshape_node, shortNames=True)[0]
    print("{0} \"{1}\" connected successfully to the {2} mesh plug of "
          "\"{3}\".".format(UiConstants.INFO_PREFIX, mesh_short_name, mesh_plug, simshape_short_name))
    return True


def get_simshape_mesh_input(selection, mesh_plug):
    """Returns a list with the inputs connected to the provided plug
    which belongs to an AdnSimshape deformer.

    Args:
        selection (list): list containing the current selection.
        mesh_plug (str): name of the plug from which to get the inputs.

    Return:
        inputs (list): List containing the input names.
    """
    if len(selection) < 2:
        return []

    simshape_node = get_simshape_deformer(selection[-1])
    if not simshape_node:
        return []

    inputs = cmds.listConnections("{0}.{1}Mesh".format(simshape_node, mesh_plug),
                                  source=True) or []

    return inputs



@undo_chunk
def remove_mesh(mesh_plug):
    """Disconnects a given mesh from one of the mesh plugs of simshape.
    The destination plug is specified by the input argument. The simshape
    deformer is retrieved from the current selected object.

    Args:
        mesh_plug (str): short name to identify the plug to disconnect
            (i.e. rest, deform or anim).
    
    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    current_selection = cmds.ls(selection=True, long=True)
    if len(current_selection) < 1:
        print("{0} Invalid selection. "
              "Please, select the mesh with AdnSimshape applied to and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    simshape_node = get_simshape_deformer(current_selection[-1])
    if not simshape_node:
        selection_short_name = cmds.ls(current_selection[-1], shortNames=True)[0]
        print("{0} Could not find a valid AdnSimshape deformer assigned to "
              "\"{1}\".".format(UiConstants.ERROR_PREFIX, selection_short_name))
        return False
    inputs = cmds.listConnections("{0}.{1}Mesh".format(simshape_node, mesh_plug),
                                  source=True) or []
    if not inputs:
        print("{0} Input connections to the {1} mesh plug not found. "
              "Nothing to remove.".format(UiConstants.WARNING_PREFIX, mesh_plug))
        return True

    cmds.disconnectAttr("{0}.outMesh".format(inputs[0]),
                        "{0}.{1}Mesh".format(simshape_node, mesh_plug))

    input_short_name = cmds.ls(inputs[0], shortNames=True)[0]
    simshape_short_name = cmds.ls(simshape_node, shortNames=True)[0]
    print("{0} \"{1}\" disconnected successfully from the {2} mesh plug of "
          "\"{3}\".".format(UiConstants.INFO_PREFIX, input_short_name, mesh_plug, simshape_short_name))
    return True


@undo_chunk
def simshape_debug_toggle():
    """Toggle the simshape debug option.
    
    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    current_selection = cmds.ls(selection=True, long=True)
    if not current_selection:
        print("{0} Selection is empty. Please, select a mesh with an AdnSimshape "
              "deformer assigned to and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    current_selection = current_selection[0]
    current_context = cmds.currentCtx()
    simshape = None
    node_history = cmds.listHistory(current_selection)
    simshape_nodes = [x for x in node_history if cmds.nodeType(x) == DeformerTypes.SIMSHAPE]
    if len(simshape_nodes) > 0:
        simshape = simshape_nodes[0]
    if simshape is None:
        selection_short_name = cmds.ls(current_selection, shortNames=True)[0]
        print("{0} Could not find an AdnSimshape deformer assigned to "
              "the selected node \"{1}\". Please, select a mesh with "
              "an AdnSimshape deformer assigned to and try again."
              "".format(UiConstants.ERROR_PREFIX, selection_short_name))
        return False

    if not check_playback(simshape):
        return True

    is_drawing = cmds.getAttr("{0}.drawActivation".format(simshape))

    # Not drawing, then switch to enable
    if not is_drawing:
        cmds.setAttr("{0}.drawActivation".format(simshape), True)
        cmds.setToolTo(current_context)
        cmds.select(current_selection, replace=True)
        if "colorSet1" not in (cmds.polyColorSet(query=True, allColorSets=True) or []):
            cmds.polyColorSet(colorSet="colorSet1", create=True)
        cmds.polyColorSet(colorSet="colorSet1", currentColorSet=True)
        print("{0} Activation debug mode ON.".format(UiConstants.INFO_PREFIX))

        # Material switch
        assign_default_shading_group = True
        selected = cmds.ls(current_selection, long=True, dag=True,
                           objectsOnly=True, shapes=True)
        selected = selected[0] if selected else []
        cmds.setAttr("{0}.displayColors".format(selected), True)
        shading_group = cmds.listConnections(selected, type="shadingEngine") or []
        if shading_group:
            assign_default_shading_group = False
            shading_group_uuid = cmds.ls(shading_group, uuid=True)
            shading_group_uuid = shading_group_uuid[0] if shading_group_uuid else []
            init_shading_group_uuid = cmds.ls("initialShadingGroup", uuid=True)
            init_shading_group_uuid = init_shading_group_uuid[0] if init_shading_group_uuid else []
            if shading_group_uuid and shading_group_uuid != init_shading_group_uuid:
                assign_default_shading_group = True
                cmds.setAttr("{0}.originalShadingGroup".format(simshape),
                             shading_group_uuid, type="string")
        if assign_default_shading_group:
            cmds.sets(selected, edit=True, forceElement="initialShadingGroup")

    # It is drawing, then switch to disable
    else:
        print("{0} Activation debug mode OFF.".format(UiConstants.INFO_PREFIX))
        if not restore_material(simshape, current_selection):
            print("{0} Disabling the activation debug mode on \"{1}\" "
                  "tried to reassign the original shader but could not restore it "
                  "successfully.".format(UiConstants.WARNING_PREFIX, simshape))

    cmds.setToolTo(current_context)
    cmds.select(current_selection, replace=True)
    return True


def get_collider_and_simshape(selection):
    """Get the collider and the AdnSimshape node.
       The expected selection order is supposed to be:
       1) Collider to connect (source).
       2) AdnSimshape node to connect to (target).

    Args:
        selection (list): Current selection.
    
    Returns:
        str: the name of the collider to connect to the AdnSimshape node.
        str: the name of the AdnSimshape node to connect the collider to.
    """
    simshape = None
    collider = None
    if not selection:
        return collider, simshape
    
    if len(selection) >= 2:
        collider = selection[0]
        simshape_object = selection[1]
    else:
        simshape_object = selection[0]

    node_history = cmds.listHistory(simshape_object)
    simshape_nodes = [x for x in node_history if cmds.nodeType(x) == DeformerTypes.SIMSHAPE]

    if not simshape_nodes:
        return collider, simshape
    
    return collider, simshape_nodes[0]


@undo_chunk
def connect_collider(is_rest=False):
    """Connect a collider to the AdnSimshape node.
       Selection order:
       1) Collider to connect (source).
       2) AdnSimshape node to connect to (target).

    Args:
        is_rest (bool, optional): Flag to check if a rest collider will be added.
            Defaults to False.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    collider_word = "Rest collider" if is_rest else "Collider"
    current_selection = cmds.ls(selection=True, long=True)

    collider, simshape = get_collider_and_simshape(current_selection)

    if not simshape or not collider:
        print("{0} No valid selection provided. Please retry adding the collider. "
              "Please, select 2 meshes in the following order: "
              "1) {1} mesh, 2) Mesh with AdnSimshape applied to."
              "".format(UiConstants.ERROR_PREFIX, collider_word))
        return False

    if not check_playback(simshape):
        return True

    rest_word = "Rest" if is_rest else ""
    collision_mesh = "{0}.collision{1}Mesh".format(simshape, rest_word)
    collision_mesh_matrix = "{0}.collision{1}MeshMatrix".format(simshape, rest_word)
    collision_mesh_connections = cmds.listConnections(collision_mesh) or []
    collision_mesh_matrix_connections = cmds.listConnections(collision_mesh) or []

    # Check collider vertices
    inverse_rest_word = "Rest" if not is_rest else ""
    check_collision_mesh = "{0}.collision{1}Mesh".format(simshape, inverse_rest_word)
    check_collision_mesh_connections = cmds.listConnections(check_collision_mesh) or []
    if check_collision_mesh_connections:
        # If the other collider is connected check the amount of vertices
        num_vertices_collider_connected = cmds.polyEvaluate(check_collision_mesh_connections[0], vertex=True)
        num_vertices_collider_to_connect = cmds.polyEvaluate(collider, vertex=True)
        if num_vertices_collider_connected != num_vertices_collider_to_connect:
            rest_collider_word = "rest " if is_rest else ""
            inverse_rest_collider_word = "rest " if not is_rest else ""
            print("{0} Collider not added because of an "
                  "inconsistency in the vertex count between the {1}collider "
                  "provided and the {2}collider already connected."
                  "".format(UiConstants.ERROR_PREFIX, rest_collider_word, inverse_rest_collider_word))
            return False

    if collision_mesh_connections or collision_mesh_matrix_connections:
        colliders = list(set(collision_mesh_connections + collision_mesh_matrix_connections))
        collider_str = ', '.join(str(col) for col in colliders)
        if len(colliders) > 1:
            collider_str = collider_str[:-2]
        word1 = "is" if len(colliders) == 1 else "are"
        word2 = "it" if len(colliders) == 1 else "them"
        button_name = "\"Remove Rest Collider\" menu" if is_rest else "remove collider shelf"
        rest_collider_word = "rest " if is_rest else ""
        print("{0} \"{1}\" {2} already connected to the \"{3}\" node. "
              "To add a new {4}collider, please remove {5} using "
              "the {6} button, and try again"
              "".format(UiConstants.ERROR_PREFIX, collider_str, word1, simshape,
                        rest_collider_word, word2, button_name))
        return False

    world_mesh = "{0}.worldMesh[0]".format(collider)
    world_matrix = "{0}.worldMatrix[0]".format(collider)
    cmds.connectAttr(world_mesh, collision_mesh, force=True)
    cmds.connectAttr(world_matrix, collision_mesh_matrix, force=True)
    selection_short_name = cmds.ls(collider, shortNames=True)[0]
    simshape_short_name = cmds.ls(simshape, shortNames=True)[0]
    print("{0} {1} \"{2}\" has been connected successfully to "
          "\"{3}\".".format(UiConstants.INFO_PREFIX, collider_word,
                            selection_short_name, simshape_short_name))
    return True


@undo_chunk
def disconnect_collider(is_rest=False):
    """Disconnect a collider to the AdnSimshape node. Selection should contain the
    mesh with AdnSimshape assigned.

    Args:
        is_rest (bool, optional): Flag to check if a rest collider will be added.
            Defaults to False.
    
    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()

    # Check selection
    current_selection = cmds.ls(selection=True, long=True)
    if len(current_selection) < 1:
        print("{0} Invalid selection. "
              "Please, select the mesh with AdnSimshape applied to and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    simshape = get_simshape_deformer(current_selection[-1])
    if not simshape:
        selection_short_name = cmds.ls(current_selection[-1], shortNames=True)[0]
        print("{0} Could not find a valid AdnSimshape deformer assigned to "
              "\"{1}\".".format(UiConstants.ERROR_PREFIX, selection_short_name))
        return

    if not check_playback(simshape):
        return True

    # Check connections
    rest_word = "Rest" if is_rest else ""
    collision_mesh = "{0}.collision{1}Mesh".format(simshape, rest_word)
    collision_mesh_matrix = "{0}.collision{1}MeshMatrix".format(simshape, rest_word)
    collision_mesh_has_connections = cmds.connectionInfo(collision_mesh, isDestination=True)
    collision_mesh_matrix_has_connections = cmds.connectionInfo(collision_mesh_matrix, isDestination=True)
    simshape_short_name = cmds.ls(simshape, shortNames=True)[0]
    rest_collider_word = "rest " if is_rest else ""

    if not collision_mesh_has_connections and not collision_mesh_matrix_has_connections:
        print("{0} No {1}colliders are connected to the \"{2}\" node."
              "".format(UiConstants.ERROR_PREFIX, rest_collider_word, simshape_short_name))
        return False

    # Disconnect collider plugs
    if collision_mesh_has_connections:
        source = cmds.connectionInfo(collision_mesh, sourceFromDestination=True)
        if source:
            cmds.disconnectAttr(source, collision_mesh)

    if collision_mesh_matrix_has_connections:
        source = cmds.connectionInfo(collision_mesh_matrix, sourceFromDestination=True)
        if source:
            cmds.disconnectAttr(source, collision_mesh_matrix)

    collider_word = "Rest collider" if is_rest else "Collider"
    print("{0} {1} has been disconnected successfully from "
          "\"{2}\".".format(UiConstants.INFO_PREFIX, collider_word, simshape_short_name))
    return True


def check_selection_activation(selection):
    """Checks if the selection contains 2 nodes and if they are in order: AdnEdgeEvaluator
    first and then AdnSimshape.

    Args:
        selection (list): Selection list contained the currently selected objects.

    Returns:
        bool: check if the selection is following the requirements.
    """
    if len(selection) != 2:
        print("{0} Wrong number of nodes selected ({1}). "
              "Please, select in the following order: "
              "1) AdnEdgeEvaluator node, 2) AdnSimshape node."
              "".format(UiConstants.ERROR_PREFIX, len(selection)))
        return False
    
    if cmds.nodeType(selection[0]) != "AdnEdgeEvaluator" or cmds.nodeType(selection[1]) != DeformerTypes.SIMSHAPE:
        print("{0} Wrong node types selected or incorrect order. "
              "Please, select in the following order: "
              "1) AdnEdgeEvaluator node, 2) AdnSimshape node."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    
    return True


@undo_chunk
def connect_activations():
    """Makes the connection between the compression attribute of AdnEdgeEvaluator and
    the activation plug of the AdnSimshape node.

    Both nodes have to be selected in order. 

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Get the nodes
    selection = cmds.ls(selection=True, dagObjects=False,
                        long=True, noIntermediate=True)
    if not check_selection_activation(selection):
        return False
    simshape_node = selection[1]
    edge_evaluator_node = selection[0]
    edge_evaluator_attr = "{0}.compression".format(edge_evaluator_node)
    simshape_attr = "{0}.activationList[0].activation".format(simshape_node)

    # Check if the parent plug is connected. 
    if cmds.connectionInfo(simshape_attr, isDestination=True):
        source = cmds.connectionInfo(simshape_attr, sourceFromDestination=True)
        if source:
            cmds.disconnectAttr(source, simshape_attr)

    cmds.connectAttr(edge_evaluator_attr, simshape_attr)
    cmds.setAttr("{0}.activationMode".format(simshape_node), 1)

    evaluator_short_name = cmds.ls(edge_evaluator_node, shortNames=True)[0]
    simshape_short_name = cmds.ls(simshape_node, shortNames=True)[0]
    print("{0} \"{1}\" has been connected successfully to \"{2}\"."
          "".format(UiConstants.INFO_PREFIX, evaluator_short_name, simshape_short_name))
    return True
    

@undo_chunk
def disconnect_activations():
    """Makes the disconnection between the compression attribute of AdnEdgeEvaluator and
    the activation plug of the AdnSimshape node.

    Both nodes have to be selected in order. A connection is needed.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Get the nodes
    selection = cmds.ls(selection=True, dagObjects=False,
                        long=True, noIntermediate=True)
    if not check_selection_activation(selection):
        return False
    simshape_node = selection[1]
    edge_evaluator_node = selection[0]
    evaluator_short_name = cmds.ls(edge_evaluator_node, shortNames=True)[0]
    simshape_short_name = cmds.ls(simshape_node, shortNames=True)[0]
    simshape_attr = "{0}.activationList[0].activation".format(simshape_node)
    edge_evaluator_attr = "{0}.compression".format(edge_evaluator_node)

    # Disconnect
    if cmds.connectionInfo(simshape_attr, isDestination=True):
        source = cmds.connectionInfo(simshape_attr, sourceFromDestination=True)
        if source:            
            if source != edge_evaluator_attr:
                print("{0} AdnSimshape node \"{1}\" is not connected to AdnEdgeEvaluator \"{2}\"."
                      "".format(UiConstants.ERROR_PREFIX, simshape_short_name, evaluator_short_name))
                return False
            else:
                cmds.disconnectAttr(source, simshape_attr)
                cmds.setAttr("{0}.activationMode".format(simshape_node), 2)
                cmds.select(clear=True)
                print("{0} \"{1}\" has been disconnected successfully from \"{2}\"."
                      "".format(UiConstants.INFO_PREFIX, evaluator_short_name, simshape_short_name))
                return True
        else:
            print("{0} Missing connection to the \"{1}\" node."
                  "".format(UiConstants.ERROR_PREFIX, simshape_short_name))
            return False
    
    return True


def restore_material(simshape_node, current_selection=None):
    """Removes color auxiliar nodes used at activation debugging.
    Restores the previous shading material before the activations debugging.

    Args:
        simshape_node (str): Name of the simshape node which mesh material is
            about to be restored.
        current_selection (list, optional): Selection of objects at scene.
            Defaults to None.
    Returns:
        bool: True if the material was properly restored, False otherwise.
    """
    material_restored = True
    cmds.setAttr("{0}.drawActivation".format(simshape_node), False)

    # Material switch
    selected = list()
    if current_selection:
        # Get shape based on selection
        selected = cmds.ls(current_selection, long=True, dag=True, objectsOnly=True, shapes=True)
    else:
        # Get shape based on deformer node
        history = cmds.listHistory(simshape_node, future=True)
        selected = cmds.ls(history, long=True, dag=True, objectsOnly=True, shapes=True)
    selected = selected[0] if selected else []
    if not selected:
        return False

    cmds.setAttr("{0}.displayColors".format(selected), False)
    original_shading_group_uuid = cmds.getAttr("{0}.originalShadingGroup".format(simshape_node))
    current_shading_group = cmds.listConnections(selected, type="shadingEngine") or []
    if not current_shading_group:
        return False

    current_shading_group_uuid = cmds.ls(current_shading_group, uuid=True)
    current_shading_group_uuid = current_shading_group_uuid[0] if current_shading_group_uuid else []
    init_shading_group_uuid = cmds.ls("initialShadingGroup", uuid=True)
    init_shading_group_uuid = init_shading_group_uuid[0] if init_shading_group_uuid else []
    if not init_shading_group_uuid:
        return False

    data_check = current_shading_group_uuid and original_shading_group_uuid
    if data_check and current_shading_group_uuid == init_shading_group_uuid:
        original_shading_group = cmds.ls(original_shading_group_uuid, long=True)
        if original_shading_group:
            original_shading_group = original_shading_group[0]
            cmds.sets(selected, edit=True, forceElement=original_shading_group)
        else:
            cmds.sets(selected, edit=True, forceElement="initialShadingGroup")
            material_restored = False
        cmds.setAttr("{0}.originalShadingGroup".format(simshape_node), "", type="string")

    return material_restored
