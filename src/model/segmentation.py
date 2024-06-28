from skimage import data, io, segmentation, color
import numpy as np
import skimage.graph as graph
import matplotlib.pyplot as plt
from skimage import morphology
from skimage import filters
import cv2
import logging

def segment(image, n_segments=800, compactness=0.1, min_lum=0.2, min_size=500, quality=0.5):
    image = color.rgb2gray(image)
    # scale image to quality
    width, height = image.shape[1], image.shape[0]
    dsize = (int(width * quality), int(height * quality))
    image = cv2.resize(image, dsize=dsize, interpolation=cv2.INTER_CUBIC)

    # Compute a mask
    mask = image > min_lum
    mask = morphology.remove_small_objects(mask, min_size=min_size)

    if mask.sum() == 0:
        logging.warning("No mask found, returning empty segments")
        return np.zeros((width, height), dtype=int), []

    # Perform SLIC segmentation
    segments = segmentation.slic(image, n_segments=n_segments, compactness=compactness, mask=mask, channel_axis=None)

    edges = filters.sobel(image)
    edges_rgb = color.gray2rgb(edges)

    g = graph.rag_boundary(segments, edges)
    lc = graph.show_rag(segments, g, edges_rgb, img_cmap=None, edge_cmap='viridis', edge_width=1.2)

    segments = cv2.resize(segments, dsize=(width, height), interpolation=cv2.INTER_NEAREST)

    return segments, lc
