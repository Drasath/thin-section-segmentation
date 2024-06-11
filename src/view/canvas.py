from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from skimage import segmentation
from skimage import color
from skimage import io
import cv2

import logging

class Canvas(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(600, 600)
        self.revisions = []
        self.q_image = QImage()
        self.q_image.fill(Qt.white)
        self.image = np.ndarray
        self.parent = parent
        self.lastPoint = QPoint()
        self.is_pressed = False
        self.is_moving = False
        self.show_borders = False

    def setImage(self, image: np.ndarray):
        if self.show_borders:
            image = segmentation.mark_boundaries(image, self.parent.segments, color=(0, 1, 0))
            image = (image * 255).astype(np.uint8) # REVIEW - Is there a better way to do this? LH
            # TODO - add overlay line contours

        self.revisions.append(self.image)

        self.q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.resizeImage()
        self.update()

    def resizeImage(self):
        width, height = self.q_image.width(), self.q_image.height()
        if width > height:
            self.q_image = self.q_image.scaledToWidth(self.width())
        else:
            self.q_image = self.q_image.scaledToHeight(self.height())
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        rect = event.rect()
        qp.drawImage(rect, self.q_image, rect)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            pass
            # Select segment

    def resizeEvent(self, event):
        self.resizeImage()

    def selectSegment(self, selectedIndex):
        mask = self.parent.segments == selectedIndex + 1 # FIXME - This + 1 is a botch. LH
        self.image[mask] = (255, 0, 0)
        self.setImage(self.image)

    def openFile(self, filename):
        self.revisions.clear()
        self.image = io.imread(filename, plugin='pil')

        if self.image is None:
            logging.error(f"Could not open file {filename}")
            return

        self.image = color.gray2rgb(self.image)
        
        # REVIEW - Might be usefull for later. LH
        # img = io.imread(filename)
        # plt.contour(img, origin='image')
        # plt.show()

        self.setImage(self.image)

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

    def toggleBorders(self):
        self.show_borders = not self.show_borders
        self.setImage(self.image)
