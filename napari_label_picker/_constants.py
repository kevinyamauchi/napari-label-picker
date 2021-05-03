import numpy as np

FACE_NORMALS = {
    "x_pos": np.array([0, 0, 1]),
    "x_neg": np.array([0, 0, -1]),
    "y_pos": np.array([0, 1, 0]),
    "y_neg": np.array([0, -1, 0]),
    "z_pos": np.array([1, 0, 0]),
    "z_neg": np.array([-1, 0, 0]),
}

FACE_INTERCEPTS = {
    "x_pos": [2, 1],
    "x_neg": [2, 0],
    "y_pos": [1, 1],
    "y_neg": [1, 0],
    "z_pos": [0, 1],
    "z_neg": [0, 0],
}
