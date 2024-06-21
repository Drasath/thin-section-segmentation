from model.modifier import Modifier
from skimage.morphology import *
import logging
from skimage import filters, graph, color
import numpy as np

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

class RAGModifier(Modifier):
    def __init__(self):
        super().__init__("RAG", "segments")
        self.inputs = []

    def apply(self, image=None, segments=None, parameters=None):
        logging.info("Applying RAG modifier...")
        image = color.rgb2gray(image)
        edges = filters.sobel(image)

        g = graph.rag_boundary(segments, edges)
        g = graph.rag_mean_color(image, segments, mode='similarity')
        segments = graph.merge_hierarchical(segments, g, thresh=parameters['Threshold'], rag_copy=False, in_place_merge=True, merge_func=merge_mean_color, weight_func=weight_mean_color)
        return segments
