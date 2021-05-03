from napari_plugin_engine import napari_hook_implementation

from .qt_picker import QtPickerWidget


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return (QtPickerWidget, {"area": "right", "name": "picker widget"})