from .erosion import ErosionModifier
from .dilation import DilationModifier
from .opening import OpeningModifier
from .closing import ClosingModifier
from .darken import DarkenModifier
from .watershed import WatershedModifier
from .histogram_equalization import HistogramEqualizationModifier

modifiers = [ErosionModifier(), DilationModifier(), OpeningModifier(), ClosingModifier(), DarkenModifier(), WatershedModifier(), HistogramEqualizationModifier()]