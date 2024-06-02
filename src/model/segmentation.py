from skimage import data, io, segmentation, color
import numpy as np
import skimage.graph as graph
import matplotlib.pyplot as plt
from skimage import morphology

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

def segment(filename, n_segments=500, compactness=0.1, min_lum=0.2, min_size=500):    
    image = io.imread(filename, plugin='pil')
    
    # Compute a mask
    mask = morphology.remove_small_holes(
        morphology.remove_small_objects(image < min_lum, min_size), min_size
    )
    mask = morphology.opening(mask, morphology.disk(3))

    # Perform SLIC segmentation
    segments = segmentation.slic(image, n_segments=n_segments, compactness=compactness, channel_axis=None)

    # Merge segments with region adjacency graph
    g = graph.rag_mean_color(image, segments, mode='similarity')
    segments = graph.merge_hierarchical(segments, g, thresh=35, rag_copy=False, in_place_merge=True, merge_func=merge_mean_color, weight_func=weight_mean_color)

    # out = color.label2rgb(labels, image, kind='avg', bg_label=0)
    # out = segmentation.mark_boundaries(out, labels, (0, 0, 0))
    # plt.imshow(out)
    # plt.show()

    return segments

if __name__ == "__main__":
    image = io.imread("./data/example.png")
    a = segment(image)