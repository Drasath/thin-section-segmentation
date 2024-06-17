from model.modifier import Modifier
from skimage import segmentation, color
import logging

import matplotlib.pyplot as plt

class SLICModifier(Modifier):
    def __init__(self):
        super().__init__("SLIC sub-segmentation", "segments")
        self.inputs = [{"name": "n_segments", "type": "int", "min": 1, "max": 100, "default": 5},
                       {"name": "compactness", "type": "float", "min": 0.0, "max": 10.0, "default": 10.0, "decimals": 1}]

    def apply(self, image=None, segments=None, parameters=None):
        image = color.rgb2gray(image)
        logging.info("Applying SLIC sub-segmentation modifier...")
        
        mask = segments != 0
        plt.imshow(mask)
        plt.show()

        return segmentation.slic(image, n_segments=parameters["n_segments"], compactness=parameters["compactness"], mask=mask, channel_axis=None) + parameters["start_label"]