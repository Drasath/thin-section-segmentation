from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import logging

class Canvas(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(600, 600)
        self.revisions = []
        self.image = QImage()
        self.image.fill(Qt.white)
        self.parent = parent
        self.lastPoint = QPoint()
        self.is_pressed = False
        self.is_moving = False

    def setImage(self, image):
        self.revisions.append(self.image)
        self.image = image

        # Scale image to fit the window keep track of the resize for later
        width, height = self.image.width(), self.image.height()
        if width > height:
            self.image = self.image.scaledToWidth(self.width())
        else:
            self.image = self.image.scaledToHeight(self.height())
        
        self.sizeChange = (self.width()/width, self.height()/height)

        self.update()

    def openFile(self, filename):
        self.revisions.clear()
        self.image = QImage(filename)

        if self.image.isNull():
            return
        
        # REVIEW - Might be usefull for later. LH
        # img = io.imread(filename)
        # plt.contour(img, origin='image')
        # plt.show()

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

    def moveImage(self, pos):
        self.image = self.image.transformed(QTransform().translate(pos.x(), pos.y()))
        self.update()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.is_pressed = True
            logging.info(f"Mouse pressed at {self.lastPoint}")
            

    def mouseMoveEvent(self, event):
        if self.is_pressed:
            self.is_moving = True
            self.moveImage(event.pos())
        self.lastPoint = event.pos()

    def mouseReleaseEvent(self, event):
        # If the using is moving the mouse, we need to move the image
        if self.is_moving:
            self.moveImage(event.pos())
            self.is_moving = False

    def undo(self):
        if self.revisions:
            self.image = self.revisions.pop()
            self.update()

    def reset(self):
        if self.revisions:
            self.image = self.revisions[0]
            self.revisions.clear()
            self.update()
