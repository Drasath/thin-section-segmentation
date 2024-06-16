from model.modifier import Modifier
from skimage import exposure, color, img_as_float
import logging

import matplotlib.pyplot as plt

class HistogramEqualizationModifier(Modifier):
    def __init__(self):
        super().__init__("Histogram Equalization", "image")
        self.inputs = []

    def apply(self, image=None, segments=None, parameters=None):
        image = color.rgb2gray(image)
        logging.info("Applying Histogram Equalization modifier...")
        
        return color.gray2rgb(exposure.equalize_hist(image) * 255).astype('uint8')