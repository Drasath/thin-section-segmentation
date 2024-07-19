from model.modifier import Modifier
from skimage.morphology import *
import logging

class OpeningModifier(Modifier):
    def __init__(self):
        super().__init__("Opening", "segments")
        self.inputs = [{"name": "Footprint size", "type": "int", "min": 0, "max": 100, "default": 5}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Opening modifier...")
        return binary_opening(segments, disk(parameters["Footprint size"]))