"""
K-Program: Sequential application of K-operators.

A K-program is a finite sequence of operators applied left-to-right.
"""

from typing import List, Sequence
from kmath.core.state import KState
from kmath.core.operators import KOperator


class KProgram:
    """
    A K-program is a finite sequence of operators applied left-to-right.
    
    The program P = [O_1, O_2, ..., O_n] applies operators sequentially:
    P(s) = O_n(...O_2(O_1(s)))
    """
    
    def __init__(self, ops: Sequence[KOperator]):
        """
        Initialize a K-program.
        
        Args:
            ops: Sequence of K-operators to apply in order
        """
        self.ops = list(ops)
    
    def step(self, state: KState) -> KState:
        """
        Execute one step of the program (apply all operators once).
        
        Args:
            state: Input K-state
            
        Returns:
            State after applying all operators in sequence
        """
        current_state = state
        for op in self.ops:
            current_state = op(current_state)
        return current_state
    
    def run(self, state: KState, steps: int) -> KState:
        """
        Run the program for multiple steps.
        
        Args:
            state: Initial K-state
            steps: Number of times to apply the full operator sequence
            
        Returns:
            Final state after `steps` iterations
        """
        current_state = state
        for _ in range(steps):
            current_state = self.step(current_state)
        return current_state
    
    def trajectory(self, state: KState, steps: int) -> List[KState]:
        """
        Generate the trajectory of states over multiple steps.
        
        Args:
            state: Initial K-state
            steps: Number of steps to run
            
        Returns:
            List of states [s_0, s_1, ..., s_steps]
        """
        trajectory = [state]
        current_state = state
        for _ in range(steps):
            current_state = self.step(current_state)
            trajectory.append(current_state)
        return trajectory
    
    def __len__(self) -> int:
        """Return the number of operators in the program."""
        return len(self.ops)
    
    def __repr__(self) -> str:
        """String representation of the program."""
        return f"KProgram(operators={len(self.ops)})"
