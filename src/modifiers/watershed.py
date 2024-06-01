from model.modifier import Modifier

class WatershedModifier(Modifier):
    def __init__(self):
        super().__init__("Watershed")
        self.inputs = [{"name": "distance", "type": "float", "min": 0, "max": 100, "default": 1, "decimals": 2},
                       {"name": "markers", "type": "marker"}]

    def apply(self, image, markers):
        pass
