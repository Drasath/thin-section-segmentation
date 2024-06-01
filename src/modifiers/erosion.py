from model.modifier import Modifier

class ErosionModifier(Modifier):
    def __init__(self):
        super().__init__("Erosion")
        self.inputs = [{"name": "cval", "type": "float", "min": 0, "max": 100, "default": 1, "decimals": 2}]

    def apply(self, image, markers):
        pass
