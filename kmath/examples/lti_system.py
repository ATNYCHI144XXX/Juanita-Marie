"""
Linear Time-Invariant (LTI) System embedding in K-Math framework.

Implements the discrete-time LTI system:
    x_{t+1} = A x_t + B u_t
"""

import numpy as np
from kmath.core.state import KState
from kmath.core.operators import KOperator


class LTISystem:
    """
    Linear Time-Invariant system: x_{t+1} = A x_t + B u_t
    
    Embedded in K-Math as a single-node system where:
    - The node state is x_t
    - The context is u_t (control input)
    - The operator applies the linear transformation
    """
    
    def __init__(self, A: np.ndarray, B: np.ndarray):
        """
        Initialize LTI system.
        
        Args:
            A: State transition matrix (n x n)
            B: Control input matrix (n x m)
        """
        self.A = np.array(A)
        self.B = np.array(B)
        
        if self.A.ndim != 2 or self.A.shape[0] != self.A.shape[1]:
            raise ValueError("A must be a square matrix")
        
        if self.B.ndim != 2 or self.B.shape[0] != self.A.shape[0]:
            raise ValueError("B must have the same number of rows as A")
        
        self.state_dim = self.A.shape[0]
        self.control_dim = self.B.shape[1]
    
    def create_initial_state(self, x0: np.ndarray, u0: np.ndarray = None) -> KState:
        """
        Create initial K-state from state and control vectors.
        
        Args:
            x0: Initial state vector (n,)
            u0: Initial control vector (m,). If None, uses zeros.
            
        Returns:
            K-state representation
        """
        if u0 is None:
            u0 = np.zeros(self.control_dim)
        
        return KState(
            nodes={'x': np.array(x0)},
            edges={},
            labels={'lti_system'},
            context=np.array(u0)
        )
    
    def get_operator(self) -> KOperator:
        """
        Get the K-operator implementing the LTI dynamics.
        
        Returns:
            K-operator that applies x_{t+1} = A x_t + B u_t
        """
        def lti_step(state: KState) -> KState:
            x_t = state.nodes['x']
            u_t = state.context if state.context is not None else np.zeros(self.control_dim)
            
            # Apply LTI dynamics
            x_next = self.A @ x_t + self.B @ u_t
            
            # Create next state (control remains the same)
            return KState(
                nodes={'x': x_next},
                edges={},
                labels=state.labels,
                context=u_t
            )
        
        return KOperator(lti_step)
    
    def simulate(self, x0: np.ndarray, control_sequence: np.ndarray) -> np.ndarray:
        """
        Simulate the LTI system with a control sequence.
        
        Args:
            x0: Initial state (n,)
            control_sequence: Control inputs (T x m) for T time steps
            
        Returns:
            State trajectory (T+1 x n)
        """
        T = len(control_sequence)
        trajectory = np.zeros((T + 1, self.state_dim))
        trajectory[0] = x0
        
        operator = self.get_operator()
        state = self.create_initial_state(x0, control_sequence[0])
        
        for t in range(T):
            # Update control
            state.context = control_sequence[t]
            
            # Apply operator
            state = operator(state)
            trajectory[t + 1] = state.nodes['x']
        
        return trajectory
    
    def compute_eigenvalues(self) -> np.ndarray:
        """
        Compute eigenvalues of the state transition matrix A.
        
        Returns:
            Array of eigenvalues
        """
        return np.linalg.eigvals(self.A)
    
    def is_stable(self) -> bool:
        """
        Check if the LTI system is stable (all eigenvalues inside unit circle).
        
        Returns:
            True if stable, False otherwise
        """
        eigenvalues = self.compute_eigenvalues()
        return np.all(np.abs(eigenvalues) < 1.0)
