"""
Stability analysis utilities for K-Math framework.
"""

from typing import Optional
import numpy as np
from kmath.core.state import KState
from kmath.core.operators import KOperator


def check_lyapunov_stability(
    operator: KOperator,
    fixed_point: KState,
    lyapunov_func: Optional[callable] = None,
    epsilon: float = 1e-3,
    num_samples: int = 10
) -> bool:
    """
    Basic Lyapunov stability check for a fixed point.
    
    Tests if small perturbations around the fixed point remain bounded.
    
    Args:
        operator: K-operator to check stability for
        fixed_point: Fixed point to check stability around
        lyapunov_func: Optional Lyapunov function V(s). If None, uses L2 norm.
        epsilon: Perturbation size
        num_samples: Number of random perturbations to test
        
    Returns:
        True if stable (all perturbations remain bounded), False otherwise
    """
    if lyapunov_func is None:
        # Default: L2 norm of all node states
        def lyapunov_func(state: KState) -> float:
            total = 0.0
            for node_state in state.nodes.values():
                total += np.sum(node_state ** 2)
            return np.sqrt(total)
    
    # Compute Lyapunov value at fixed point
    v_fixed = lyapunov_func(fixed_point)
    
    # Test random perturbations
    for _ in range(num_samples):
        # Create perturbed state
        perturbed = fixed_point.copy()
        for node_id in perturbed.nodes:
            perturbation = epsilon * np.random.randn(*perturbed.nodes[node_id].shape)
            perturbed.nodes[node_id] = perturbed.nodes[node_id] + perturbation
        
        # Apply operator
        next_state = operator(perturbed)
        
        # Check if Lyapunov function decreased or stayed bounded
        v_next = lyapunov_func(next_state)
        v_perturbed = lyapunov_func(perturbed)
        
        # If V increased significantly, not stable
        if v_next > v_perturbed + epsilon:
            return False
    
    return True


def compute_jacobian_eigenvalues(
    operator: KOperator,
    fixed_point: KState,
    epsilon: float = 1e-6
) -> np.ndarray:
    """
    Compute eigenvalues of the Jacobian at a fixed point (numerical approximation).
    
    Args:
        operator: K-operator
        fixed_point: Fixed point to linearize around
        epsilon: Step size for finite differences
        
    Returns:
        Array of eigenvalues
    """
    # Flatten all node states into a single vector
    node_ids = sorted(fixed_point.nodes.keys())
    n = sum(fixed_point.nodes[nid].size for nid in node_ids)
    
    # Compute Jacobian numerically
    jacobian = np.zeros((n, n))
    
    for i, node_id in enumerate(node_ids):
        node_state = fixed_point.nodes[node_id]
        for j in range(node_state.size):
            # Perturb state
            perturbed = fixed_point.copy()
            perturbed.nodes[node_id] = node_state.copy()
            perturbed.nodes[node_id].flat[j] += epsilon
            
            # Apply operator
            next_state = operator(perturbed)
            
            # Compute derivative
            col_idx = sum(fixed_point.nodes[nid].size for nid in node_ids[:i]) + j
            row_idx = 0
            for k, nid in enumerate(node_ids):
                diff = (next_state.nodes[nid] - operator(fixed_point).nodes[nid]) / epsilon
                size = diff.size
                jacobian[row_idx:row_idx+size, col_idx] = diff.flat
                row_idx += size
    
    # Compute eigenvalues
    eigenvalues = np.linalg.eigvals(jacobian)
    return eigenvalues


def is_asymptotically_stable(
    operator: KOperator,
    fixed_point: KState,
    epsilon: float = 1e-6
) -> bool:
    """
    Check if a fixed point is asymptotically stable using eigenvalue test.
    
    A fixed point is asymptotically stable if all eigenvalues of the Jacobian
    have magnitude less than 1.
    
    Args:
        operator: K-operator
        fixed_point: Fixed point to check
        epsilon: Numerical epsilon for Jacobian computation
        
    Returns:
        True if asymptotically stable, False otherwise
    """
    try:
        eigenvalues = compute_jacobian_eigenvalues(operator, fixed_point, epsilon)
        return np.all(np.abs(eigenvalues) < 1.0)
    except Exception:
        # If Jacobian computation fails, fall back to False
        return False
