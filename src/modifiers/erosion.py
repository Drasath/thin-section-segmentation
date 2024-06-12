from model.modifier import Modifier
from skimage.morphology import erosion, disk
from skimage.util import img_as_ubyte
import logging

class ErosionModifier(Modifier):
    def __init__(self):
        super().__init__("Erosion")
        self.inputs = [{"name": "Footprint size", "type": "int", "min": 0, "max": 100, "default": 1}]

    def apply(self, image=None, segments=None, parameters=None):
        # TODO - Implement erosion modifier. LH       
        logging.info("Applying Erosion modifier...")
        return erosion(img_as_ubyte(image))