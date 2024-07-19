from model.modifier import Modifier
from skimage.morphology import *
import logging

class ErosionModifier(Modifier):
    def __init__(self):
        super().__init__("Erosion", "segments")
        self.inputs = [{"name": "Footprint size", "type": "int", "min": 0, "max": 100, "default": 5}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Erosion modifier...")
        return binary_erosion(segments, disk(parameters["Footprint size"]))