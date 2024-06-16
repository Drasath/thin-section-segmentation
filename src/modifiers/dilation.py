from model.modifier import Modifier
from skimage.morphology import *
import logging

class DilationModifier(Modifier):
    def __init__(self):
        super().__init__("Dilation", "segments")
        self.inputs = [{"name": "Footprint size", "type": "int", "min": 0, "max": 100, "default": 1}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Dilation modifier...")
        return binary_dilation(segments, disk(parameters["Footprint size"]))