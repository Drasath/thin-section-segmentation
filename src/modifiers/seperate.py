from model.modifier import Modifier
from skimage.morphology import *
import logging
import cv2

class SeparateModifier(Modifier):
    def __init__(self):
        super().__init__("Separate", "segments")
        self.inputs = []

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying Separate modifier...")

        # Find all non connected segments
        contours = cv2.findContours(segments, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Assign a unique label to each segment
        for i, contour in enumerate(contours):
            cv2.drawContours(segments, contour, -1, i + 1, -1)

        return 