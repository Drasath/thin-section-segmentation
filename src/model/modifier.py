import numpy as np

class Modifier():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.inputs = []

    def apply(self, image:np.ndarray, segments, parameters:dict):
        pass

    def __str__(self):
        return f"{self.name}: {self.value}"

    def __repr__(self):
        return f"{self.name}: {self.value}"
