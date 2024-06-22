from model.modifier import Modifier
from skimage.morphology import *
import logging
from skimage import filters, graph, color
import numpy as np

# SECTION - Taken from https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_rag_merge.html
def weight_boundary(graph, src, dst, n):
    """
    Handle merging of nodes of a region boundary region adjacency graph.

    This function computes the `"weight"` and the count `"count"`
    attributes of the edge between `n` and the node formed after
    merging `src` and `dst`.


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
        A dictionary with the "weight" and "count" attributes to be
        assigned for the merged node.

    """
    default = {'weight': 0.0, 'count': 0}

    count_src = graph[src].get(n, default)['count']
    count_dst = graph[dst].get(n, default)['count']

    weight_src = graph[src].get(n, default)['weight']
    weight_dst = graph[dst].get(n, default)['weight']

    count = count_src + count_dst
    return {
        'count': count,
        'weight': (count_src * weight_src + count_dst * weight_dst) / count,
    }


def merge_boundary(graph, src, dst):
    """Call back called before merging 2 nodes.

    In this case we don't need to do any computation here.
    """
    pass

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
        
        segments = graph.merge_hierarchical(
            segments,
            g,
            thresh=parameters['Threshold'],
            rag_copy=False,
            in_place_merge=True,
            merge_func=merge_boundary,
            weight_func=weight_boundary
        )
        return segments
