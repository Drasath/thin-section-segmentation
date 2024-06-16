from model.modifier import Modifier
from skimage import segmentation
import logging
import numpy as np
from skimage import feature
from scipy import ndimage

class WatershedModifier(Modifier):
    def __init__(self):
        super().__init__("Watershed", "segments")
        self.inputs = [{"name": "Region shape", "type": "int", "min": 0, "max": 100, "default": 6}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Watershed modifier...")
        distance = ndimage.distance_transform_edt(segments)
        peak_idx = feature.peak_local_max(
            distance,
            footprint=np.ones((parameters['Region shape'], parameters['Region shape'])),
            labels=segments,
        )
        peak_mask = np.zeros_like(segments, dtype=bool)
        peak_mask[tuple(peak_idx.T)] = True

        markers = ndimage.label(peak_mask)[0]
        labels = segmentation.watershed(-distance, markers, mask=segments)
        return labels