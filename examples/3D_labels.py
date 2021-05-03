from skimage import data
from scipy import ndimage as ndi
import napari
import numpy as np

from napari_label_picker.label_selection_model import LabelSelectionModel

blobs = data.binary_blobs(length=128, volume_fraction=0.1, n_dim=3)
viewer = napari.view_image(blobs.astype(float), name='blobs', visible=False)
labeled = ndi.label(blobs)[0]
labels_layer = viewer.add_labels(labeled, name='blob ID')

napari.run()
