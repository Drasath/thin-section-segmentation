import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from . import mainwindow

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    gui = mainwindow.MainWindow()
    gui.show()
    return app.exec_()
