import numpy as np

from ._constants import FACE_INTERCEPTS


def clamp_point_to_bbox(point: np.ndarray, bbox: np.ndarray):
    clamped_point = np.clip(point, bbox[:, 0], bbox[:, 1])

    return clamped_point


def face_intercepts_from_bbox(bbox: np.ndarray):

    face_intercepts = {k: bbox[v[0], v[1]] for k, v in FACE_INTERCEPTS.items()}

    return face_intercepts


def get_view_direction_in_scene_coordinates(
    view: "vispy.scene.widgets.viewbox.ViewBox",
) -> np.ndarray:
    """calculate the unit vector pointing in the direction of the view

    Adapted From:
    https://stackoverflow.com/questions/37877592/
        get-view-direction-relative-to-scene-in-vispy/37882984

    Parameters
    ----------
    view : vispy.scene.widgets.viewbox.ViewBox
        The vispy view box object to get the view direction from.

    Returns
    -------
    view_vector : np.ndarray
        Unit vector in the direction of the view in scene coordinates
    """
    tform = view.scene.transform
    w, h = view.canvas.size
    # in homogeneous screen coordinates
    screen_center = np.array([w / 2, h / 2, 0, 1])
    d1 = np.array([0, 0, 1, 0])
    point_in_front_of_screen_center = screen_center + d1
    p1 = tform.imap(point_in_front_of_screen_center)
    p0 = tform.imap(screen_center)
    assert abs(p1[3] - 1.0) < 1e-5
    assert abs(p0[3] - 1.0) < 1e-5
    d2 = p1 - p0
    assert abs(d2[3]) < 1e-5
    # in 3D screen coordinates
    d3 = d2[0:3]
    d4 = d3 / np.linalg.norm(d3)
    return d4[[2, 1, 0]]


def vector_axis_aligned_plane_intersection(
    face_intercept: float, face_normal: np.ndarray, point: np.ndarray, dir: np.ndarray
) -> np.ndarray:
    # find the axis the plane exists in
    plane_axis = np.argwhere(face_normal)

    # get the intersection coordinate
    t = (face_intercept - point[plane_axis]) / dir[plane_axis]
    intersection_point = point + t * dir

    return intersection_point


def bounding_box_to_face_vertices(bounding_box: np.ndarray) -> dict:
    """
    From a layer bounding box (N, 2), N=ndim, return a dictionary containing
    the vertices of each face of the bounding_box
    """
    x_min, x_max = bounding_box[-1, :]
    y_min, y_max = bounding_box[-2, :]
    z_min, z_max = bounding_box[-3, :]

    # we offset the min/max by -/+ 1 so the faces
    # are just outside of the data (i.e., visible)
    x_min -= 1
    y_min -= 1
    z_min -= 1
    x_max += 1
    y_max += 1
    z_max += 1

    face_coords = {
        "x_pos": np.array(
            [
                [z_min, y_min, x_max],
                [z_min, y_max, x_max],
                [z_max, y_max, x_max],
                [z_max, y_min, x_max],
            ]
        ),
        "x_neg": np.array(
            [
                [z_min, y_min, x_min],
                [z_min, y_max, x_min],
                [z_max, y_max, x_min],
                [z_max, y_min, x_min],
            ]
        ),
        "y_pos": np.array(
            [
                [z_min, y_max, x_min],
                [z_min, y_max, x_max],
                [z_max, y_max, x_max],
                [z_max, y_max, x_min],
            ]
        ),
        "y_neg": np.array(
            [
                [z_min, y_min, x_min],
                [z_min, y_min, x_max],
                [z_max, y_min, x_max],
                [z_max, y_min, x_min],
            ]
        ),
        "z_pos": np.array(
            [
                [z_max, y_min, x_min],
                [z_max, y_min, x_max],
                [z_max, y_max, x_max],
                [z_max, y_max, x_min],
            ]
        ),
        "z_neg": np.array(
            [
                [z_min, y_min, x_min],
                [z_min, y_min, x_max],
                [z_min, y_max, x_max],
                [z_min, y_max, x_min],
            ]
        ),
    }
    return face_coords
