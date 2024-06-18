from skimage import data, io, segmentation, color
import numpy as np
import skimage.graph as graph
import matplotlib.pyplot as plt
from skimage import morphology
from skimage import filters
import cv2

# TODO - Refactor. LH
# TODO - Expand on this, allow for setting the parameters and have multiple options. LH

# SECTION - Taken from https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_rag_merge.html
def merge_mean_color(graph, src, dst):
    """Callback called before merging two nodes of a mean color distance graph.

    This method computes the mean color of `dst`.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    """
    graph.nodes[dst]['total color'] += graph.nodes[src]['total color']
    graph.nodes[dst]['pixel count'] += graph.nodes[src]['pixel count']
    graph.nodes[dst]['mean color'] = (
        graph.nodes[dst]['total color'] / graph.nodes[dst]['pixel count']
    )

def weight_mean_color(graph, src, dst, n):
    """Callback to handle merging nodes by recomputing mean color.

    The method expects that the mean color of `dst` is already computed.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    n : int
        A neighbor of `src` or `dst` or both.

    Returns
    -------
    data : dict
        A dictionary with the `"weight"` attribute set as the absolute
        difference of the mean color between node `dst` and `n`.
    """

    diff = graph.nodes[dst]['mean color'] - graph.nodes[n]['mean color']
    diff = np.linalg.norm(diff)
    return {'weight': diff}

#!SECTION

def segment(image, n_segments=800, compactness=0.1, min_lum=0.2, min_size=500, quality=0.5):
    image = color.rgb2gray(image)
    # scale image to quality
    width, height = image.shape[1], image.shape[0]
    dsize = (int(width * quality), int(height * quality))
    image = cv2.resize(image, dsize=dsize, interpolation=cv2.INTER_CUBIC)

    # Compute a mask
    mask = image > min_lum
    mask = morphology.remove_small_objects(mask, min_size=min_size)

    # Perform SLIC segmentation
    segments = segmentation.slic(image, n_segments=n_segments, compactness=compactness, mask=mask, channel_axis=None)

    edges = filters.sobel(image)
    edges_rgb = color.gray2rgb(edges)

    g = graph.rag_boundary(segments, edges)
    lc = graph.show_rag(segments, g, edges_rgb, img_cmap=None, edge_cmap='viridis', edge_width=1.2)

    g = graph.rag_mean_color(image, segments, mode='similarity')
    segments = graph.merge_hierarchical(segments, g, thresh=0.3, rag_copy=False, in_place_merge=True, merge_func=merge_mean_color, weight_func=weight_mean_color)

    segments = cv2.resize(segments, dsize=(width, height), interpolation=cv2.INTER_NEAREST)

    return segments, lc

def apply_rag(image, segments, threshold=0.08):
    image = color.rgb2gray(image)
    edges = filters.sobel(image)
    g = graph.rag_boundary(segments, edges)
    # Merge segments with region adjacency graph
    g = graph.rag_mean_color(image, segments, mode='similarity')
    segments = graph.merge_hierarchical(segments, g, thresh=threshold, rag_copy=False, in_place_merge=True, merge_func=merge_mean_color, weight_func=weight_mean_color)
    return segments
