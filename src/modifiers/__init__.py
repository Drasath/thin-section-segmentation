from .erosion import ErosionModifier
from .dilation import DilationModifier
from .opening import OpeningModifier
from .closing import ClosingModifier
from .watershed import WatershedModifier
from .slic import SLICModifier
from .histogram_equalization import HistogramEqualizationModifier

modifiers = [ErosionModifier(), DilationModifier(), OpeningModifier(), ClosingModifier(), WatershedModifier(), SLICModifier(), HistogramEqualizationModifier()]