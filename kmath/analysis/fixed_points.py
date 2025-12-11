"""
Fixed point and cycle detection utilities.
"""

from typing import Optional, List
from kmath.core.state import KState
from kmath.core.operators import KOperator
from kmath.core.recurrence import KRecurrence


def find_fixed_point(
    operator: KOperator,
    initial_state: KState,
    max_iterations: int = 1000,
    tolerance: float = 1e-6
) -> Optional[KState]:
    """
    Find a fixed point of an operator: O(s*) = s*.
    
    Args:
        operator: K-operator to find fixed point for
        initial_state: Starting point for iteration
        max_iterations: Maximum number of iterations
        tolerance: Convergence tolerance
        
    Returns:
        Fixed point if found, None otherwise
    """
    recurrence = KRecurrence(recurrence_map=operator)
    return recurrence.find_fixed_point(initial_state, max_iterations, tolerance)


def find_cycle(
    operator: KOperator,
    initial_state: KState,
    max_iterations: int = 1000,
    tolerance: float = 1e-6
) -> Optional[List[KState]]:
    """
    Detect cycles in operator iteration using Floyd's algorithm.
    
    Args:
        operator: K-operator to detect cycles for
        initial_state: Starting point
        max_iterations: Maximum iterations
        tolerance: Tolerance for state comparison
        
    Returns:
        Cycle as list of states if found, None otherwise
    """
    recurrence = KRecurrence(recurrence_map=operator)
    return recurrence.find_cycle(initial_state, max_iterations, tolerance)
