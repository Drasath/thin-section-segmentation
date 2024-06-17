from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from skimage import segmentation
from skimage import color
from skimage import io

import logging

class Canvas(QWidget):
    """
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO - Clean this up. LH
        self.revisions = []
        self.markers = []
        self.q_image = QImage()
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

    def set_image(self, image: np.ndarray):
        if self.show_borders:
            image = segmentation.mark_boundaries(image, self.parent.segments, color=(0, 1, 0))
            image = (image * 255).astype(np.uint8) # REVIEW - Is there a better way to do this? LH

        self.revisions.append(self.image)

        logging.debug(f"Setting image with shape {image.shape}")

        self.q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.resize_image()
        self.update()

    def resize_image(self):
        width, height = self.q_image.width(), self.q_image.height()
        if width > height:
            self.q_image = self.q_image.scaledToWidth(self.width())
        else:
            self.q_image = self.q_image.scaledToHeight(self.height())
        
        if self.q_image.width() != 0:
            self.resizeScale = width / self.q_image.width()

        self.update()

    def draw_markers(self, qp):
        pass
        # for marker in self.markers:
        #     qp.setPen(QPen(Qt.red, 1))
        #     qp.drawPoint(marker)

  # TODO - Refactor this method. LH
    def paintEvent(self, event):
        qp = QPainter(self)
        rect = event.rect()
        qp.drawImage(rect, self.q_image, rect)
        if self.show_rag:
            gradient = QConicalGradient()
            gradient.setCenter(rect.center())
            gradient.setAngle(90)
            gradient.setColorAt(0, Qt.red)
            gradient.setColorAt(0.5, Qt.green)

            qp.setPen(QPen(gradient, 4.0))
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

    def resizeEvent(self, event):
        self.resize_image()

    def select_segment(self, selectedIndex):
        mask = self.parent.segments == selectedIndex
        copy = self.image.copy()
        copy[mask] = (255, 0, 0)
        self.set_image(copy)
        self.parent.selected_region_properties.setText(str(self.parent.regionprops[selectedIndex - 1]))
        self.selectedIndex = selectedIndex

    def open_file(self, filename):
        self.revisions.clear()
        self.image = io.imread(filename, plugin='pil')

        if self.image is None:
            logging.error(f"Could not open file {filename}")
            return

        # self.image = color.gray2rgb(self.image)
        
        # REVIEW - Might be usefull for later. LH
        # img = io.imread(filename)
        # plt.contour(img, origin='image')
        # plt.show()

        self.set_image(self.image)

    def move_image(self, pos):
        self.image = self.image.transformed(QTransform().translate(pos.x(), pos.y()))
        self.update()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.lastPoint = event.pos() * self.resizeScale
            self.is_pressed = True
            self.update()
            self.select_segment(self.parent.segments[self.lastPoint.y()][self.lastPoint.x()])

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.zoomedIn = not self.zoomedIn
            self.zoom_in(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.revisions.append(self.image.copy())
            self.is_pressed = False
            self.update()
            
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            
            self.zoom_in(event.pos())
        else:
            self.zoom_out(event.pos())

    def zoom_in(self, cursorPos):
        # Zoom towards the mouse position
        logging.info("Zooming in")

    def zoom_out(self, cursorPos):
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

    def toggle_borders(self):
        self.show_borders = not self.show_borders
        self.setImage(self.image)

    def toggle_RAG(self):
        self.show_rag = not self.show_rag
        self.update()
