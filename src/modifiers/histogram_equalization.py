from model.modifier import Modifier
from skimage import exposure, color
import logging

import matplotlib.pyplot as plt

class HistogramEqualizationModifier(Modifier):
    def __init__(self):
        super().__init__("Histogram Equalization", "image")
        self.inputs = []

    def apply(self, image=None, segments=None, parameters=None):
        image = color.rgb2gray(image)
        logging.info("Applying Histogram Equalization modifier...")

        # Local Histogram Equalization
        image = exposure.equalize_adapthist(image, clip_limit=0.03)

        return color.gray2rgb(image * 255).astype('uint8')