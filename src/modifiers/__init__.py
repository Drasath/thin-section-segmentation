from .erosion import ErosionModifier
from .dilation import DilationModifier
from .opening import OpeningModifier
from .closing import ClosingModifier
from .watershed import WatershedModifier
from .slic import SLICModifier
from .histogram_equalization import HistogramEqualizationModifier
from .region_adjacency_graph import RAGModifier

modifiers = [ErosionModifier(), DilationModifier(), OpeningModifier(), ClosingModifier(), SLICModifier(), HistogramEqualizationModifier()]
rag_modifier = RAGModifier()