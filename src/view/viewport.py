from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
from skimage import io, color, segmentation, graph
import logging

from constants import *
class Viewport(QWidget):
    """
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = 1200
        self.setMinimumSize(size, size)

        self.reset()

    def reset(self):
        size = 1200
        self.transform = QTransform()
        self.image: np.ndarray = None
        self.q_image = QImage(size, size, QImage.Format_RGB888)
        self.q_image.fill(Qt.gray)
        self.segments: np.ndarray = None
        self.rag: graph.LineCollection = None
        self.show_borders: bool = False
        self.show_rag: bool = False
        self.show_colors: bool = False
        self.show_overlay: bool = False
        self.resize_scale: float = 1
        self.mouse_moved = False
        self.zoom_level = 1
        self.selected_segments = []

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_pos = event.pos()
            self.mouse_moved = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            qApp.changeOverrideCursor(Qt.ClosedHandCursor)
            self.mouse_moved = True
            dx, dy = (event.x() - self.last_pos.x()) / self.resize_scale, (event.y() - self.last_pos.y()) / self.resize_scale
            self.transform.translate(dx, dy)
            self.update()
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mouse_moved:
                self.mouse_moved = False
                qApp.restoreOverrideCursor()
                # Move image or marker depending on mode
                
            else:
                # Select region or add marker depending on mode
                if self.segments is None:
                    return
                mouse_pos = self.transform.inverted()[0].map(event.pos()) * self.resize_scale
                logging.info(f"Mouse position: {event.pos()} {mouse_pos} {self.width()} {self.height()}")
                if mouse_pos.x() < 0 or mouse_pos.x() >= self.segments.shape[1] or mouse_pos.y() < 0 or mouse_pos.y() >= self.segments.shape[0]:
                    return

                if event.modifiers() == Qt.ControlModifier:
                    self.selected_segments.append(self.segments[int(mouse_pos.y()), int(mouse_pos.x())])
                else:
                    self.selected_segments = [self.segments[int(mouse_pos.y()), int(mouse_pos.x())]]
                self.update()

    def wheelEvent(self, event):
        # TODO - Zoom towards mouse position. LH
        # TODO - Zoom away from mouse position, and towards the center. LH
        if event.angleDelta().y() > 0:
            if self.zoom_level > 500:
                return
            self.transform.translate(self.width() / 2, self.height() / 2)
            self.transform.scale(1.1, 1.1)   
            self.transform.translate(-self.width() / 2, -self.height() / 2)
            self.zoom_level *= 1.1
        else:
            if self.zoom_level < .1:
                return
            self.transform.translate(self.width() / 2, self.height() / 2)
            self.transform.scale(0.9, 0.9)   
            self.transform.translate(-self.width() / 2, -self.height() / 2)
            self.zoom_level *= 0.9
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setTransform(self.transform)
        rect = event.rect()

        self._draw_borders(qp, rect) if self.show_borders else qp.drawImage(rect, self.q_image, rect)
        
        if self.show_rag:
            self._draw_rag(qp)

        if self.show_colors:
            self._draw_colors(qp)

        if self.show_overlay:
            self._draw_overlay(qp)

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
        self.q_image = self.q_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self.reset()
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
        image = np.zeros((self.image.shape[0], self.image.shape[1], 4), dtype=np.uint8)
        image[mask] = (255, 0, 0, 128)

        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGBA8888)
        q_image = q_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qp.drawImage(rect, q_image, rect)

    def _draw_borders(self, qp, rect):
        if self.segments is None:
            return

        image = segmentation.mark_boundaries(self.image, self.segments, color=(0, 1, 0), mode='inner')
        image = (image * 255).astype(np.uint8)
        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        q_image = q_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qp.drawImage(rect, q_image, rect)

    def _draw_rag(self, qp):
        if self.rag is None:
            return

    def _draw_colors(self, qp):
        if self.segments is None:
            return
        
        # Show segments in different colors
        image = np.zeros((self.image.shape[0], self.image.shape[1], 4), dtype=np.uint8)
        for i, segment in enumerate(np.unique(self.segments)):
            mask = self.segments == segment
            image[mask] = np.random.randint(0, 255, 3).tolist() + [128]

        q_image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGBA8888)
        q_image = q_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qp.drawImage(0, 0, q_image)

    def _draw_overlay(self, qp):
        overlay = QImage(str(PROJECT_DIRECTORY / "resources" / "images" / "goal.tif"))
        overlay = overlay.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qp.drawImage(0, 0, overlay)

    def toggle_borders(self):
        self.show_borders = not self.show_borders
        self.update()

    def toggle_rag(self):
        self.show_rag = not self.show_rag
        self.update()
    
    def toggle_colors(self):
        self.show_colors = not self.show_colors
        self.update()

    def toggle_overlay(self):
        self.show_overlay = not self.show_overlay
        self.update()

    def reset_transform(self):
        self.transform.reset()
        self.update()

    