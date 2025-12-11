"""
K-Recurrence: Recursive dynamics engine for K-Math.

Supports time-invariant and time-variant recurrence relations with
fixed-point and cycle detection.
"""

from typing import Callable, Optional, List, Tuple
from kmath.core.state import KState
from kmath.core.operators import KOperator
from kmath.core.program import KProgram


class KRecurrence:
    """
    Recurrence engine for recursive dynamics.
    
    Supports:
    - Time-invariant recurrence: s_{t+1} = R(s_t)
    - Time-variant recurrence: s_{t+1} = R(s_t, t)
    - Fixed-point detection
    - Cycle detection
    """
    
    def __init__(
        self,
        recurrence_map: Optional[KOperator] = None,
        time_variant_map: Optional[Callable[[KState, int], KState]] = None
    ):
        """
        Initialize recurrence engine.
        
        Args:
            recurrence_map: Time-invariant recurrence R(s) for s_{t+1} = R(s_t)
            time_variant_map: Time-variant recurrence R(s,t) for s_{t+1} = R(s_t, t)
            
        Note: Provide exactly one of recurrence_map or time_variant_map.
        """
        if (recurrence_map is None) == (time_variant_map is None):
            raise ValueError("Provide exactly one of recurrence_map or time_variant_map")
        
        self.recurrence_map = recurrence_map
        self.time_variant_map = time_variant_map
        self.is_time_invariant = recurrence_map is not None
    
    def iterate(self, state: KState, steps: int) -> KState:
        """
        Iterate the recurrence for a number of steps.
        
        Args:
            state: Initial state s_0
            steps: Number of iterations
            
        Returns:
            Final state s_steps
        """
        current_state = state
        for t in range(steps):
            if self.is_time_invariant:
                current_state = self.recurrence_map(current_state)
            else:
                current_state = self.time_variant_map(current_state, t)
        return current_state
    
    def trajectory(self, state: KState, steps: int) -> List[KState]:
        """
        Generate trajectory of states.
        
        Args:
            state: Initial state s_0
            steps: Number of iterations
            
        Returns:
            List [s_0, s_1, ..., s_steps]
        """
        traj = [state]
        current_state = state
        for t in range(steps):
            if self.is_time_invariant:
                current_state = self.recurrence_map(current_state)
            else:
                current_state = self.time_variant_map(current_state, t)
            traj.append(current_state)
        return traj
    
    def find_fixed_point(
        self,
        initial_state: KState,
        max_iterations: int = 1000,
        tolerance: float = 1e-6
    ) -> Optional[KState]:
        """
        Find a fixed point of the recurrence: R(s*) = s*.
        
        Args:
            initial_state: Starting point for iteration
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Fixed point if found, None otherwise
            
        Note: Only works for time-invariant recurrence.
        """
        if not self.is_time_invariant:
            raise ValueError("Fixed point detection only works for time-invariant recurrence")
        
        current_state = initial_state
        for _ in range(max_iterations):
            next_state = self.recurrence_map(current_state)
            
            # Check convergence
            if self._states_close(current_state, next_state, tolerance):
                return next_state
            
            current_state = next_state
        
        return None
    
    def find_cycle(
        self,
        initial_state: KState,
        max_iterations: int = 1000,
        tolerance: float = 1e-6
    ) -> Optional[List[KState]]:
        """
        Detect cycles in the recurrence using Floyd's algorithm.
        
        Args:
            initial_state: Starting point
            max_iterations: Maximum iterations
            tolerance: Tolerance for state comparison
            
        Returns:
            Cycle as list of states if found, None otherwise
            
        Note: Only works for time-invariant recurrence.
        """
        if not self.is_time_invariant:
            raise ValueError("Cycle detection only works for time-invariant recurrence")
        
        # Floyd's cycle detection (tortoise and hare)
        tortoise = initial_state
        hare = initial_state
        
        # Phase 1: Detect if cycle exists
        for _ in range(max_iterations):
            tortoise = self.recurrence_map(tortoise)
            hare = self.recurrence_map(self.recurrence_map(hare))
            
            if self._states_close(tortoise, hare, tolerance):
                break
        else:
            return None  # No cycle found
        
        # Phase 2: Find cycle start
        mu = 0  # Cycle start
        tortoise = initial_state
        while not self._states_close(tortoise, hare, tolerance):
            tortoise = self.recurrence_map(tortoise)
            hare = self.recurrence_map(hare)
            mu += 1
        
        # Phase 3: Find cycle length
        lam = 1  # Cycle length
        hare = self.recurrence_map(tortoise)
        while not self._states_close(tortoise, hare, tolerance):
            hare = self.recurrence_map(hare)
            lam += 1
        
        # Extract cycle
        cycle = []
        current = tortoise
        for _ in range(lam):
            cycle.append(current)
            current = self.recurrence_map(current)
        
        return cycle
    
    def _states_close(self, s1: KState, s2: KState, tolerance: float) -> bool:
        """
        Check if two states are close within tolerance.
        
        Args:
            s1: First state
            s2: Second state
            tolerance: Tolerance for comparison
            
        Returns:
            True if states are close, False otherwise
        """
        import numpy as np
        
        # Check nodes
        if set(s1.nodes.keys()) != set(s2.nodes.keys()):
            return False
        
        for node_id in s1.nodes:
            if not np.allclose(s1.nodes[node_id], s2.nodes[node_id], atol=tolerance):
                return False
        
        # Check edges
        if set(s1.edges.keys()) != set(s2.edges.keys()):
            return False
        
        for edge_id in s1.edges:
            if not np.allclose(s1.edges[edge_id], s2.edges[edge_id], atol=tolerance):
                return False
        
        # Check context
        if (s1.context is None) != (s2.context is None):
            return False
        
        if s1.context is not None:
            if not np.allclose(s1.context, s2.context, atol=tolerance):
                return False
        
        return True
    
    @staticmethod
    def from_program(program: KProgram) -> 'KRecurrence':
        """
        Create a recurrence from a K-program.
        
        Args:
            program: K-program defining the recurrence
            
        Returns:
            KRecurrence instance
        """
        return KRecurrence(recurrence_map=KOperator(program.step))
