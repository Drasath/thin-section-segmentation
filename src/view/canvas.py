from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from skimage import segmentation
from skimage import color
from skimage import io

import logging

class Canvas(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(600, 600)
        # TODO - Clean this up. LH
        self.revisions = []
        self.q_image = QImage()
        self.q_image.fill(Qt.white)
        self.image = np.ndarray
        self.parent = parent
        self.lastPoint = QPoint()
        self.is_pressed = False
        self.is_moving = False
        self.resizeScale = 1
        self.zoomedIn = False
        self.show_borders = False
        self.show_rag = False
        self.selectedIndex = None
        self.markers = []

    def setImage(self, image: np.ndarray):
        if self.show_borders:
            # image = segmentation.mark_boundaries(image, self.parent.segments, color=(0, 1, 0))
            labels = color.label2rgb(self.parent.segments, image=image, bg_label=0)
            image = (labels * 255).astype(np.uint8) # REVIEW - Is there a better way to do this? LH
            # TODO - add overlay line contours

        self.revisions.append(self.image)

        logging.debug(f"Setting image with shape {image.shape}")

        self.q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.resizeImage()
        self.update()

    def resizeImage(self):
        width, height = self.q_image.width(), self.q_image.height()
        if width > height:
            self.q_image = self.q_image.scaledToWidth(self.width())
        else:
            self.q_image = self.q_image.scaledToHeight(self.height())
        
        if self.q_image.width() != 0:
            self.resizeScale = width / self.q_image.width()

        self.update()

    # TODO - Refactor this method. LH
    def paintEvent(self, event):
        qp = QPainter(self)
        rect = event.rect()
        qp.drawImage(rect, self.q_image, rect)
        if self.show_rag:
            qp.setPen(QPen(Qt.red, 1))
            segments = self.parent.lc.get_segments()
            for segment in segments:
                x1, y1 = segment[0] * 1/self.resizeScale
                x2, y2 = segment[1] * 1/self.resizeScale
                qp.drawLine(x1, y1, x2, y2)
        if self.zoomedIn:
            # Zoom towards the selected segment
            center = self.parent.regionprops[self.selectedIndex - 1].centroid
            matrix = QTransform()
            matrix.translate(center[1], center[0])
            matrix.scale(2, 2)
            matrix.translate(-center[1], -center[0])
            self.q_image = self.q_image.transformed(matrix)
            # self.q_image = self.q_image.scaled(self.q_image.width() * 2, self.q_image.height() * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def drawMarkers(self, qp):
        pass
        # for marker in self.markers:
        #     qp.setPen(QPen(Qt.red, 1))
        #     qp.drawPoint(marker)

    def drawLine(self, qp):
        qp.setPen(QPen(Qt.red, 1))
        qp.drawLine(0, 0, 100, 100)

    def resizeEvent(self, event):
        self.resizeImage()

    def selectSegment(self, selectedIndex):
        mask = self.parent.segments == selectedIndex
        copy = self.image.copy()
        copy[mask] = (255, 0, 0)
        self.setImage(copy)
        self.parent.selected_region_properties.setText(str(self.parent.regionprops[selectedIndex - 1]))
        self.selectedIndex = selectedIndex

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
            self.lastPoint = event.pos() * self.resizeScale
            self.is_pressed = True
            self.update()
            # logging.info(f"pressed at {self.parent.segments[self.lastPoint.y()][self.lastPoint.x()]}")
            self.selectSegment(self.parent.segments[self.lastPoint.y()][self.lastPoint.x()])

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.zoomedIn = not self.zoomedIn
            self.zoomIn(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.revisions.append(self.image.copy())
            self.is_pressed = False
            self.update()
            
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            
            self.zoomIn(event.pos())
        else:
            self.zoomOut(event.pos())

    def zoomIn(self, cursorPos):
        # Zoom towards the mouse position
        logging.info("Zooming in")

    def zoomOut(self, cursorPos):
        # Zoom towards the mouse position
        logging.info("Zooming out")

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

    def toggleRAG(self):
        self.show_rag = not self.show_rag
        self.update()