"""
K-Math: Recursive Mathematics Framework

A framework for modeling complex systems as iterated operator dynamics over structured state spaces.
"""

from kmath.core.state import KState
from kmath.core.operators import (
    KOperator,
    KStructuralOperator,
    KNumericalOperator,
    KContextOperator,
    KMetaOperator,
    KNodeUpdateOperator,
    KEdgeUpdateOperator,
    KLabelOperator,
    KContextUpdateOperator,
)
from kmath.core.program import KProgram
from kmath.core.recurrence import KRecurrence

__version__ = "0.1.0"
__all__ = [
    "KState",
    "KOperator",
    "KStructuralOperator",
    "KNumericalOperator",
    "KContextOperator",
    "KMetaOperator",
    "KNodeUpdateOperator",
    "KEdgeUpdateOperator",
    "KLabelOperator",
    "KContextUpdateOperator",
    "KProgram",
    "KRecurrence",
]
