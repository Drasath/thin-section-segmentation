from skimage import segmentation
import skimage.io as io
from skimage import color
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QImage
from skimage import morphology

# TODO - Refactor. LH
# TODO - Expand on this, allow for setting the parameters and have multiple options. LH

def segment(filename, n_segments=100, compactness=10, min_lum=0.7, min_size=500):
    image = io.imread(filename)

    # Compute a mask
    lum = color.rgb2gray(image)
    mask = morphology.remove_small_holes(
        morphology.remove_small_objects(lum < min_lum, min_size), min_size
    )
    mask = morphology.opening(mask, morphology.disk(3))
    segments = segmentation.slic(image, n_segments=n_segments, compactness=compactness, mask=mask)
    return segments

if __name__ == "__main__":
    image = io.imread("./data/example.png")
    a = segment(image)