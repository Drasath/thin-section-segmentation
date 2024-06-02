class Modifier():
    def __init__(self, name):
        self.name = name
        self.inputs = []

    def apply(self, image, segments, parameters):
        pass

    def __str__(self):
        return f"{self.name}: {self.value}"

    def __repr__(self):
        return f"{self.name}: {self.value}"
