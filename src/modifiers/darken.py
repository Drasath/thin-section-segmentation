from model.modifier import Modifier
import logging

class DarkenModifier(Modifier):
    def __init__(self):
        super().__init__("Darken", "image")
        self.inputs = [{"name": "Percentage", "type": "float", "min": 0, "max": 100, "default": 10, "decimals": 2}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Darken modifier...")
        return (image * (1 - parameters["Percentage"] / 100)).astype(image.dtype)