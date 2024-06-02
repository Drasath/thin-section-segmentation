from model.modifier import Modifier
import logging

class WatershedModifier(Modifier):
    def __init__(self):
        super().__init__("Watershed")
        self.inputs = [{"name": "distance", "type": "float", "min": 0, "max": 100, "default": 1, "decimals": 2},
                       {"name": "markers", "type": "marker"}]

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Watershed modifier...")
        print(len(segments))
