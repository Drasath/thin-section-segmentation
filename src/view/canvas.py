from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Canvas(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(600, 600)
        self.revisions = []
        self.image = QImage()
        self.image.fill(Qt.white)
        self.parent = parent

    def openFile(self, filename):
        self.revisions.clear()
        self.image = QImage(filename)

        if self.image.isNull():
            return

        # Scale image to fit the window keep track of the resize for later
        width, height = self.image.width(), self.image.height()
        if width > height:
            self.image = self.image.scaledToWidth(self.width())
        else:
            self.image = self.image.scaledToHeight(self.height())
        
        self.sizeChange = (self.width()/width, self.height()/height)

        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        rect = event.rect()
        qp.drawImage(rect, self.image, rect)

    def undo(self):
        if self.revisions:
            self.image = self.revisions.pop()
            self.update()

    def reset(self):
        if self.revisions:
            self.image = self.revisions[0]
            self.revisions.clear()
            self.update()
