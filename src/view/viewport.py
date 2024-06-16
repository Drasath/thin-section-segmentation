from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from skimage import io, color, segmentation, graph
import logging

class Viewport(QWidget):
    """
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = 1200
        self.setFixedSize(size, size)

        self.image: np.ndarray = None
        self.q_image = QImage(size, size, QImage.Format_RGB888)
        self.q_image.fill(Qt.gray)
        self.segments: np.ndarray = None
        self.rag: graph.LineCollection = None
        self.show_borders: bool = False
        self.show_rag: bool = False
        self.resize_scale: float = 1
        self.mouse_moved = False
        self.selected_segments = []

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mouse_moved = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mouse_moved:
                self.mouse_moved = False
                # Move image or marker depending on mode
            else:
                # Select region or add marker depending on mode
                if self.segments is None:
                    return
                if event.modifiers() == Qt.ControlModifier:
                    self.selected_segments.append(self.segments[int(event.y() * self.resize_scale), int(event.x() * self.resize_scale)])
                else:
                    self.selected_segments = [self.segments[int(event.y() * self.resize_scale), int(event.x() * self.resize_scale)]]
                self.update()

    def wheelEvent(self, event):
        logging.info(f"Wheel event: {event.angleDelta().y()}")

    def paintEvent(self, event):
        qp = QPainter(self)
        rect = event.rect()

        self._draw_borders(qp) if self.show_borders else qp.drawImage(rect, self.q_image, rect)
        
        if self.show_rag:
            self._draw_rag(qp)

        if len(self.selected_segments) > 0:
            for segment in self.selected_segments:
                self._draw_segment(qp, rect, segment)

    def resizeEvent(self, event):
        self._resize_image()
        self.update()

    def set_segments(self, segments: np.ndarray):
        self.segments = segments
        self.update()

    def set_image(self, image: np.ndarray):
        self.image = image
        self.q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.update()

    def _resize_image(self):
        width, height = self.q_image.width(), self.q_image.height()
        if width > height:
            self.q_image = self.q_image.scaledToWidth(self.width())
        else:
            self.q_image = self.q_image.scaledToHeight(self.height())

        if self.q_image.width() != 0:
            self.resize_scale = width / self.q_image.width()

    def load_image(self, image_path: str):
        self.image = io.imread(image_path, plugin='pil')
        self.image = color.gray2rgb(self.image)
        if self.image is None:
            logging.error(f"Could not load image from {image_path}")
            return
        logging.info(f"Image loaded from {image_path}")
        
        self.set_image(self.image)

    def _draw_point(self, qp, point: QPoint):
        qp.setPen(QPen(Qt.yellow, 3))
        qp.drawPoint(point)

    def _draw_line(self, qp, start: QPoint, end: QPoint):
        qp.setPen(QPen(Qt.yellow, 3))
        qp.drawLine(start, end)

    def _draw_segment(self, qp, rect, segment: np.ndarray):
        if self.segments is None:
            return
        
        mask = self.segments == segment
        image = np.zeros( (self.image.shape[0], self.image.shape[1], 4), dtype=np.uint8)
        image[mask] = (255, 0, 0, 128)

        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGBA8888)
        q_image = q_image.scaled(self.width(), self.height())
        qp.drawImage(self.rect(), q_image)

    def _draw_borders(self, qp):
        if self.segments is None:
            return

        image = segmentation.mark_boundaries(self.image, self.segments, color=(0, 1, 0), mode='subpixel')
        image = (image * 255).astype(np.uint8)
        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        q_image = q_image.scaled(self.width(), self.height())
        qp.drawImage(self.rect(), q_image)

    def _draw_rag(self, qp):
        if self.rag is None:
            return

    def toggle_borders(self):
        self.show_borders = not self.show_borders
        self.update()

    def toggle_rag(self):
        self.show_rag = not self.show_rag
        self.update()
    
    