from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ParameterInput(QLineEdit):
    """
    Input field for parameter tab.
    """
    def __init__(self, input):
        super().__init__()

        # TODO - Add label to input
        self.setPlaceholderText(input["name"])

        if "default" in input:
            self.setText(str(input["default"]))

        # TODO - Add more input types
        # TODO - Implement marker input
        # TODO - Add validation and error messages
        if input["type"] == "int":
            self.setValidator(QIntValidator(input["min"], input["max"]))
        elif input["type"] == "float":
            self.setValidator(QDoubleValidator(input["min"], input["max"], input["decimals"]))
        elif input["type"] == "marker":
            self.setReadOnly(True)
            self.setPlaceholderText("Select a marker")
        

class ParameterTab(QWidget):
    """
    Widget containing input fields for the parameters of a modifier. 
    """
    def __init__(self, parent, modifier):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.set_modifier(modifier)

    def set_modifier(self, modifier):
        self.clear()
        self.modifier = modifier
        for input in modifier.inputs:
            self.layout.addWidget(ParameterInput(input))

    def clear(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

    def get_parameters(self):
        parameters = {}
        i = 0
        for parameter in self.modifier.inputs:
            input = self.layout.itemAt(i).widget()
            if parameter['type'] == "int":
                parameters[input.placeholderText()] = int(input.text())
            elif parameter['type'] == "float":
                parameters[input.placeholderText()] = float(input.text())
            i += 1
        
        return parameters