from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QWidget

from .label_selection_model import LabelSelectionModel

class QtPickerWidget(QWidget):
    """The QWdiget containing the controls for the picker tool

    Parameters
    ----------
    napari_viewer : napari.viewer.Viewer
        The parent napari viewer

    Attributes
    ----------
    """

    def __init__(self, viewer: 'napari.viewer.Viewer'):
        super().__init__()
        self.viewer = viewer
        self.model = LabelSelectionModel(viewer)


        # Create a combobox for selecting layers
        self.layer_combo_box = QComboBox(self)
        self._selected_layer = None
        self.layer_combo_box.currentIndexChanged.connect(self.on_layer_selection)
        self.initialize_layer_combobox()

        self.viewer.layers.events.inserted.connect(self.on_add_layer)
        self.viewer.layers.events.removed.connect(self.on_remove_layer)

    @property
    def selected_layer(self):
        return self._selected_layer

    @selected_layer.setter
    def selected_layer(self, selected_layer):
        self.model.attach_layer(self.viewer.layers[selected_layer])
        self._selected_layer = selected_layer

    def initialize_layer_combobox(self):
        """Populates the combobox with all layers that contain properties"""
        layer_names = [
            layer.name
            for layer in self.viewer.layers
            if type(layer).__name__ == "Labels"
        ]
        self.layer_combo_box.addItems(layer_names)

        if self.selected_layer is None:
            self.selected_layer = layer_names[0]
        index = self.layer_combo_box.findText(self.selected_layer, Qt.MatchExactly)
        self.layer_combo_box.setCurrentIndex(index)

    def on_add_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is added to the viewer LayerList.
        """
        layer_name = event.value.name
        layer = self.viewer.layers[layer_name]
        if type(layer).__name__ == "Labels":
            self.layer_combo_box.addItem(layer_name)

    def on_remove_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is removed from the viewer LayerList.
        """
        layer_name = event.value.name

        index = self.layer_combo_box.findText(layer_name, Qt.MatchExactly)
        # findText returns -1 if the item isn't in the ComboBox
        # if it is in the ComboBox, remove it
        if index != -1:
            self.layer_combo_box.removeItem(index)

            # get the new layer selection
            index = self.layer_combo_box.currentIndex()
            layer_name = self.layer_combo_box.itemText(index)
            if layer_name != self.selected_layer:
                self.selected_layer = layer_name

    def on_layer_selection(self, index: int):
        """Callback function that updates the table when a
        new layer is selected in the combobox.
        """
        if index != -1:
            layer_name = self.layer_combo_box.itemText(index)
            self.selected_layer = layer_name