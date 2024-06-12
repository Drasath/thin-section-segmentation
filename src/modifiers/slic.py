from model.modifier import Modifier
import logging
from skimage import segmentation

class SLICModifier(Modifier):
    def __init__(self):
        super().__init__("SLIC")
        self.inputs = [{"name": "n segments", "type": "int", "min": 0, "max": 10000, "default": 800},
                       {"name": "compactness", "type": "float", "min": 0, "max": 100, "default": 0.1, "decimals": 2},
                       {"name": "min lum", "type": "float", "min": 0, "max": 1, "default": 0.2, "decimals": 2},
                       {"name": "min size", "type": "int", "min": 0, "max": 2000, "default": 500}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying SLIC modifier...")
        segments = segmentation.slic(image, n_segments=parameters['n segments'], compactness=parameters['compactness'], channel_axis=None)
        return segments
