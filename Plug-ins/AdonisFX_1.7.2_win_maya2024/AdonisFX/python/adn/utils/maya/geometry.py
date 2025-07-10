import maya.OpenMaya as OpenMaya
import maya.cmds as cmds


def get_points_py_list(geo_name):
    """Get the vertices of a mesh using maya.OpenMaya API.

    Args:
        geo_name (str): The name of the mesh.

    Returns:
        list: A list of vertices, where each vertex is a list of coordinates.
    """
    vertices = []

    maya_sel = OpenMaya.MSelectionList()
    maya_sel.add(geo_name)
    geo_dag = OpenMaya.MDagPath()
    maya_sel.getDagPath(0, geo_dag)
    geo_fn = OpenMaya.MFnMesh(geo_dag) 
    geo_points = OpenMaya.MPointArray()
    geo_fn.getPoints(geo_points)
    geo_triangles_count = OpenMaya.MIntArray()
    geo_triangles_vertices = OpenMaya.MIntArray()
    geo_fn.getTriangles(geo_triangles_count, geo_triangles_vertices)

    points_count = geo_points.length()
    for point_index in range(points_count):
        vertices.append([
            geo_points[point_index].x,
            geo_points[point_index].y,
            geo_points[point_index].z])

    return vertices


def get_closest_point_and_uv(mesh, query_point):
    """Uses maya.OpenMaya to find the closest point on the mesh to
    target_point and retrieves the corresponding UV coordinates.

    Args:
        mesh (str): The name of the mesh.
        query_point (tuple): A 3-tuple (x, y, z) position for which
            to find the closest point.

    Returns:
        tuple: (closestPoint (MPoint), (u, v) coordinates)
    """
    # Obtain the MObject for the mesh.
    selList = OpenMaya.MSelectionList()
    selList.add(mesh)
    mesh_dag = OpenMaya.MDagPath()
    selList.getDagPath(0, mesh_dag)
    
    
    # Create an MFnMesh for API operations.
    mesh_fn = OpenMaya.MFnMesh(mesh_dag)
    mesh_points = OpenMaya.MPointArray()
    mesh_fn.getPoints(mesh_points)
    
    # Create an MPoint from the query point coordinates.
    query = OpenMaya.MPoint(query_point[0], query_point[1], query_point[2])
    closest_point = OpenMaya.MPoint()

    closest_polygon_util = OpenMaya.MScriptUtil()
    closest_polygon_util.createFromInt(-1)
    closest_polygon_ptr = closest_polygon_util.asIntPtr()
    
    # Compute the closest point on the mesh (in world space).
    mesh_fn.getClosestPoint(query, closest_point, OpenMaya.MSpace.kWorld, closest_polygon_ptr)
    closest_polygon = OpenMaya.MScriptUtil.getInt(closest_polygon_ptr)
    
    # Prepare MScriptUtil objects for retrieving U and V values.
    uv_util = OpenMaya.MScriptUtil()
    uv_util.createFromList([0.0, 0.0], 2)
    uv_point = uv_util.asFloat2Ptr()
    
    # Get the UV coordinates at the closest point
    polygon_vertices = OpenMaya.MIntArray()
    mesh_fn.getPolygonVertices(closest_polygon, polygon_vertices)
    polygon_vertices_count = polygon_vertices.length()
    polygon_average_point = OpenMaya.MPoint(0.0, 0.0, 0.0)
    for i in range(polygon_vertices_count):
        vertex_index = polygon_vertices[i]
        polygon_average_point += OpenMaya.MVector(mesh_points[vertex_index])
    if polygon_vertices_count > 0:
        polygon_average_point /= polygon_vertices_count
    mesh_fn.getClosestPoint(polygon_average_point, closest_point, OpenMaya.MSpace.kWorld)
    mesh_fn.getUVAtPoint(closest_point, uv_point, OpenMaya.MSpace.kWorld)

    u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 0)
    v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 1)
    
    return closest_point, (u, v)


def get_bounding_box_diagonal(mesh):
    """Get the diagonal length of the bounding box of a mesh.

    Args:
        mesh (str): The name of the mesh.

    Returns:
        float: The diagonal length of the bounding box.
    """
    # Get the world-space bounding box
    bbox = cmds.exactWorldBoundingBox(mesh)
    min_point = bbox[0:3]
    max_point = bbox[3:6]
    # Calculate the diagonal length
    return ((max_point[0] - min_point[0]) ** 2 +
            (max_point[1] - min_point[1]) ** 2 +
            (max_point[2] - min_point[2]) ** 2) ** 0.5
