from copy import deepcopy

from napari.layers.shapes._shapes_utils import inside_triangles
import numpy as np

from ._constants import FACE_NORMALS
from ._utils import (
    bounding_box_to_face_vertices,
    clamp_point_to_bbox,
    face_intercepts_from_bbox,
    get_view_direction_in_scene_coordinates,
    vector_axis_aligned_plane_intersection
)


class LabelSelectionModel:
    def __init__(self, viewer: 'napari.viewer.Viewer', opacity: float=0.01):
        self._viewer = viewer
        self.opacity = opacity
        self._selected_layer = None

    @property
    def selected_layer(self):
        return self._selected_layer

    def attach_layer(self, labels_layer: 'napari.layers.Labels'):
        self._selected_layer = labels_layer

        color_dict = {v: deepcopy(self.selected_layer.get_color(v)) for v in np.unique(self.selected_layer.data)}
        self.selected_layer.color = color_dict
        self.selected_layer.color_mode = 'direct'

        self.selected_layer.mouse_drag_callbacks.append(self._on_click)

    def detach_layer(self):
        if self.selected_layer is not None:
            self.selected_layer.mouse_drag_callbacks.remove(self._on_click)
            self._selected_layer = None

    def _on_click(self, layer, event):
        view_box = self._viewer._window.qt_viewer.view
        view_dir = get_view_direction_in_scene_coordinates(view_box)
        print(f'view_dir: {view_dir}')

        # Get the positino of the click and map it to the scene
        click_pos_canv = event.pos
        tform_i = self._viewer.window.qt_viewer.layer_to_visual[layer].node.get_transform(map_from="canvas", map_to="visual")
        mapped_click = tform_i.map(click_pos_canv)[[2, 1, 0]]

        tform = self._viewer.window.qt_viewer.layer_to_visual[layer].node.get_transform(map_from="visual",
                                                                               map_to="canvas")

        bbox = np.array([
            [0, layer.data.shape[0]],
            [0, layer.data.shape[1]],
            [0, layer.data.shape[2]]
        ])
        bbox_face_coords = bounding_box_to_face_vertices(bbox)
        front_face = None
        for k, v in FACE_NORMALS.items():
            if (np.dot(view_dir, v) + 0.001) < 0:
                vertices = bbox_face_coords[k]
                face_intercepts = face_intercepts_from_bbox(bbox)

                # convert the vertex coordinates to canvas coordinates
                vertices_canv = tform.map(np.asarray(vertices)[:, [2, 1, 0]])
                vertices_canv = vertices_canv[:, :2] / vertices_canv[:, 3:]
                triangle_vertices_canv = np.stack(
                    (vertices_canv[[0, 1, 2]], vertices_canv[[0, 2, 3]])
                )
                in_triangles = inside_triangles(
                    triangle_vertices_canv - click_pos_canv
                )
                if in_triangles.sum() > 0:
                    front_face = k
                    print("front: ", front_face)

            elif (np.dot(view_dir, v) + 0.001) > 0:
                vertices = bbox_face_coords[k]

                # convert the vertex coordinates to canvas coordinates
                vertices_canv = tform.map(np.asarray(vertices)[:, [2, 1, 0]])
                vertices_canv = vertices_canv[:, :2] / vertices_canv[:, 3:]
                triangle_vertices_canv = np.stack(
                    (vertices_canv[[0, 1, 2]], vertices_canv[[0, 2, 3]])
                )
                in_triangles = inside_triangles(
                    triangle_vertices_canv - click_pos_canv
                )
                if in_triangles.sum() > 0:
                    back_face = k
                    print('back: ', back_face)
        label_selected = False
        if front_face is not None:
            front_face_normal = FACE_NORMALS[front_face]
            front_face_intercept = face_intercepts[front_face]
            near_point = np.squeeze(vector_axis_aligned_plane_intersection(
                front_face_intercept,
                front_face_normal,
                mapped_click,
                -view_dir
            ))
            print("near_pos", near_point)

            back_face_normal = FACE_NORMALS[back_face]
            back_face_intercept = face_intercepts[back_face]
            far_point = np.squeeze(vector_axis_aligned_plane_intersection(
                back_face_intercept,
                back_face_normal,
                mapped_click,
                view_dir
            ))
            print("far_pos", far_point)

            sample_ray = far_point - near_point
            length_sample_vector = np.linalg.norm(sample_ray)
            increment_vector = sample_ray / (2 * length_sample_vector)
            n_iterations = int(2 * length_sample_vector)

            for i in range(n_iterations):
                sample_point = np.asarray(near_point + i * increment_vector, dtype=int)
                sample_point = clamp_point_to_bbox(sample_point, bbox)
                value = layer.data[sample_point[0], sample_point[1], sample_point[2]]
                if value != 0:
                    label_selected = True
                    break

            if value != 0:
                orig_colors = deepcopy(layer.color)
                new_color = {}

                for k, v in orig_colors.items():
                    if k != value:
                        col = v.copy()
                        col = col * [1, 1, 1, self.opacity]
                        new_color.update({k: col})
                    else:
                        new_color.update({k: v.copy()})
                layer.color = new_color
                layer.interactive = False

        yield

        # drag stuff
        if label_selected is True:
            while event.type == 'mouse_move':
                displacement = click_pos_canv[1] - event.pos[1]
                new_sample_point = np.asarray(sample_point + displacement * increment_vector, dtype=int)
                new_sample_point = clamp_point_to_bbox(new_sample_point, bbox)
                new_value = layer.data[new_sample_point[0], new_sample_point[1], new_sample_point[2]]
                print(displacement, new_value)

                if (new_value != 0) and (new_value != value):
                    value = new_value
                    new_color = {}

                    for k, v in orig_colors.items():
                        if k != value:
                            col = v.copy()
                            col = col * [1, 1, 1, self.opacity]
                            new_color.update({k: col})
                        else:
                            new_color.update({k: v.copy()})
                    layer.color = new_color
                yield

            # clean up
            layer.interactive = True
            layer.color = orig_colors


