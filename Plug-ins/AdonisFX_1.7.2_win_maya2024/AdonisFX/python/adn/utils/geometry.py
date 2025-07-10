from adn.utils.math import squared_distance


def find_extremal_vertices(vertices, centroid, direction):
    """Find the two vertices of a mesh that are extremal in the direction
    of the main axis. The two vertices are the closest to the end points
    of the line defined by the centroid and the direction vector.

    This is done by intersecting a parametric line (along the main axis) with
    the mesh's axis-aligned bounding box (AABB), determining the entry and exit
    points of that line through the box, and then selecting the mesh vertices
    closest to those two intersection points.

    The line is expressed in parametric form:
        P(t) = C + t * d
    where:
        C is the mesh centroid,
        d is the direction vector of the main axis,
        t is the scalar parameter.

    As t varies:
      - P(0) = C, the line passes through the centroid.
      - P(t) for t < 0 moves opposite to the direction vector.
      - P(t) for t > 0 moves along the direction vector.

    Args:
        vertices (list): A list of vertices, where each vertex is a list of coordinates.
        centroid (list): The centroid of the mesh as a list of coordinates.
        direction (list): The direction vector as a list of coordinates.

    Returns:
        dict: A dictionary containing the start and end vertices and their indices.
              The keys are "start_vertex", "end_vertex", "start_index", and "end_index".
              If no valid extremal vertices are found, returns None.
    """
    # Unpack centroid and direction for convenience
    centroid_x, centroid_y, centroid_z = centroid
    dir_x, dir_y, dir_z = direction

    # 1. Compute the bounding box of the mesh.
    min_x = min(v[0] for v in vertices)
    max_x = max(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)
    min_z = min(v[2] for v in vertices)
    max_z = max(v[2] for v in vertices)

    # 2. Compute intersection points of the line with the bounding box.

    # The line is defined by the parametric equation of a line: P(t) = C + t * d.
    # Where C is the centroid, d is the direction vector and t is the parameter.

    # For each axis, solve for t at the min and max boundaries.
    intersections = []  # will store tuples of (t, (x, y, z))
    eps = 1e-8  # small tolerance to avoid numerical issues
    # For each axis: 0 -> x, 1 -> y, 2 -> z.
    for axis in range(3):
        if axis == 0:
            boundaries = [min_x, max_x]
            centroid_axis = centroid_x
            dir_axis = dir_x
        elif axis == 1:
            boundaries = [min_y, max_y]
            centroid_axis = centroid_y
            dir_axis = dir_y
        else:  # axis == 2
            boundaries = [min_z, max_z]
            centroid_axis = centroid_z
            dir_axis = dir_z

        # Avoid division by zero
        if abs(dir_axis) < eps:
            continue

        for boundary in boundaries:
            # By solving centroid_axis + t * dir_axis = boundary for each face of the
            # bounding box, we find the t values at which the line intersects those faces
            t = (boundary - centroid_axis) / dir_axis
            # The corresponding P(t) gives the intersection point
            p_x = centroid_x + t * dir_x
            p_y = centroid_y + t * dir_y
            p_z = centroid_z + t * dir_z

            # Check if the intersection point lies within the bounding limits for the other axes.
            if axis == 0:
                if (min_y - eps <= p_y <= max_y + eps) and (min_z - eps <= p_z <= max_z + eps):
                    intersections.append((t, (p_x, p_y, p_z)))
            elif axis == 1:
                if (min_x - eps <= p_x <= max_x + eps) and (min_z - eps <= p_z <= max_z + eps):
                    intersections.append((t, (p_x, p_y, p_z)))
            else:  # axis == 2
                if (min_x - eps <= p_x <= max_x + eps) and (min_y - eps <= p_y <= max_y + eps):
                    intersections.append((t, (p_x, p_y, p_z)))

    # Ensure we found at least two intersections.
    if len(intersections) < 2:
        return None

    # Sort intersections by the parameter t.
    intersections.sort(key=lambda item: item[0])
    # The two endpoints are at the smallest and largest t.
    end_point_1 = intersections[0][1]
    end_point_2 = intersections[-1][1]

    # 3. Find the vertex closest to each end point.
    closest_vertex_1 = None
    closest_vertex_2 = None
    closest_index_1 = None
    closest_index_2 = None
    min_dist_1 = float('inf')
    min_dist_2 = float('inf')

    for i, v in enumerate(vertices):
        d1 = squared_distance(v, end_point_1)
        if d1 < min_dist_1:
            min_dist_1 = d1
            closest_vertex_1 = v
            closest_index_1 = i
        d2 = squared_distance(v, end_point_2)
        if d2 < min_dist_2:
            min_dist_2 = d2
            closest_vertex_2 = v
            closest_index_2 = i

    extremal_vertices_data = {
        "start_point": closest_vertex_1,
        "end_point": closest_vertex_2,
        "start_index": closest_index_1,
        "end_index": closest_index_2,
    }

    return extremal_vertices_data
