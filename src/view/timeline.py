from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import logging
from constants import *

class Timeline(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.amg = [{"name": "Node 1"}, {"name": "Node 2"}, {"name": "Node 3"}]

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Timeline"))
        self.layout().addWidget(QPushButton("Update", clicked=self.update))
        self.button_widget = QWidget()
        self.button_widget.setLayout(QHBoxLayout())
        self.layout().addWidget(self.button_widget)

    def update(self):
        self.clear()
        for node in self.amg:
            button = QPushButton()
            button.clicked.connect(lambda _, n=node: self.load_node(n["name"]))
            icon = QIcon(str(PROJECT_DIRECTORY / "resources" / "images" / "amg_default.png"))
            button.setIcon(icon)
            self.button_widget.layout().addWidget(button)

    def clear(self):
        for i in reversed(range(self.button_widget.layout().count())):
            self.button_widget.layout().itemAt(i).widget().deleteLater()

    def load_node(self, node):
        logging.info(f"Loading node: {node}")
