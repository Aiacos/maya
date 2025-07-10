import math


def compute_centroid(points):
    """Compute the centroid of a list of points.

    Args:
        points (list): A list of points, where each point is a list of coordinates.

    Returns:
        list: The centroid of the points as a list of coordinates.
    """
    num_points = len(points)
    if num_points == 0:
        return []
    dimension = len(points[0])
    centroid = [0.0] * dimension
    for p in points:
        for i in range(dimension):
            centroid[i] += p[i]
    centroid = [x / num_points for x in centroid]
    return centroid


def center_points(points, centroid):
    """Subtract the centroid from each point to center the data.

    Args:
        points (list): A list of points, where each point is a list of coordinates.
        centroid (list): The centroid to subtract from each point.

    Returns:
        list: A new list of centered points.
    """
    return [[p[i] - centroid[i] for i in range(len(centroid))] for p in points]


def compute_covariance_matrix(centered_points):
    """Compute the covariance matrix from the centered points.
    Uses the sample covariance (dividing by n-1). The covariance
    matrix is a square matrix where the element at (i, j) represents
    the covariance between the i-th and j-th dimensions. It describes
    the shape and orientation of the points distribution to allow to
    obtain the oriented bounding box.

    Args:
        centered_points (list): A list of centered points, where each
            point is a list of coordinates.

    Returns:
        list: The covariance matrix as a list of lists.
    """
    num_points = len(centered_points)
    if num_points < 2:
        return None
    dimension = len(centered_points[0])
    # Initialize a d x d matrix filled with 0's
    cov_matrix = [[0.0] * dimension for _ in range(dimension)]
    for p in centered_points:
        for i in range(dimension):
            for j in range(dimension):
                cov_matrix[i][j] += p[i] * p[j]
    factor = 1.0 / (num_points - 1)
    for i in range(dimension):
        for j in range(dimension):
            cov_matrix[i][j] *= factor
    return cov_matrix


def matrix_mult_vector(matrix, vector):
    """Multiply a square matrix by a vector.

    Args:
        matrix (list): A square matrix as a list of lists.
        vector (list): A vector as a list of coordinates.

    Returns:
        list: The resulting vector as a list of coordinates.
    """
    dimension = len(matrix)
    result = [0.0] * dimension
    for i in range(dimension):
        for j in range(len(vector)):
            result[i] += matrix[i][j] * vector[j]
    return result


def vector_length(v):
    """Return the Euclidean norm of vector v.

    Args:
        v (list): A vector as a list of coordinates.

    Returns:
        float: The Euclidean norm of the vector.
    """
    return math.sqrt(sum(x * x for x in v))


def vector_normalized(v):
    """Return the vector v normalized to unit length.

    Args:
        v (list): A vector as a list of coordinates.

    Returns:
        list: The normalized vector as a list of coordinates.
    """
    norm = vector_length(v)
    if norm == 0:
        return v
    return [x / norm for x in v]


def vector_diff(v1, v2):
    """Return the difference between two vectors.

    Args:
        v1 (list): The first vector as a list of coordinates.
        v2 (list): The second vector as a list of coordinates.

    Returns:
        float: The difference vector between the two vectors.
    """
    return [a - b for a, b in zip(v1, v2)]


def compute_principal_eigenvector(input_matrix, max_iterations=1000, tolerance=1e-9):
    """Computes the principal eigenvector of a square matrix using the
    power iteration method. The principal eigen vector is the direction
    of maximum variance in the data represented by the matrix. It corresponds
    to the largest eigenvalue of the covariance matrix and it is the principal
    component of PCA.
    

    Args:
        input_matrix (list): A square matrix represented as a list of lists.
        max_iterations (int, optional): Maximum number of power-iteration steps to run.
            Defaults to 1000.
        tolerance (float, optional): Threshold for convergence. Defaults to 1e-9.

    Returns:
        list: A unit-length vector approximating the principal eigenvector.
    """
    dimension = len(input_matrix)

    # 1) Initialize with a guess (all ones) and normalize
    eigenvector_estimate = [1.0] * dimension
    eigenvector_estimate = vector_normalized(eigenvector_estimate)

    for _ in range(max_iterations):
        # 2) Apply the matrix
        transformed_vector = matrix_mult_vector(input_matrix, eigenvector_estimate)

        # 3) Normalize the result
        next_estimate = vector_normalized(transformed_vector)

        # 4) Check for convergence
        difference_vector = vector_diff(next_estimate, eigenvector_estimate)
        difference_norm = vector_length(difference_vector)
        if difference_norm < tolerance:
            break

        # 5) Update for next iteration
        eigenvector_estimate = next_estimate

    return eigenvector_estimate


def compute_main_axis(points):
    """Given a list of points as a list or tuple of coordinates,
    compute the main axis of the set of points using PCA.
    PCA (Principal Component Analysis) is a linear dimensionality
    reduction technique that allows to find the main axis of a set
    of points. The main axis is the direction of maximum variance
    in the data.

    Args:
        points (list): A list of points, where each point is a list
            or tuple of coordinates.

    Returns:
        centroid: The centroid of the points.
        main_axis: A unit vector representing the main axis.
    """
    if not points:
        return None, None
    dimension = len(points[0])
    # Ensure all points have the same dimension
    for p in points:
        if len(p) != dimension:
            return None, None

    centroid = compute_centroid(points)
    centered_points = center_points(points, centroid)
    cov_matrix = compute_covariance_matrix(centered_points)
    main_axis = compute_principal_eigenvector(cov_matrix)
    return centroid, main_axis


def squared_distance(p1, p2):
    """Compute the squared distance between two points.

    Args:
        p1 (list): The first point as a list of coordinates.
        p2 (list): The second point as a list of coordinates.

    Returns:
        float: The squared distance between the two points.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
