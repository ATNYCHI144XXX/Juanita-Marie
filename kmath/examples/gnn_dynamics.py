"""
Graph Neural Network (GNN)-like dynamics in K-Math framework.

Implements message-passing dynamics:
    x_v^{(t+1)} = σ(W_1 x_v^{(t)} + Σ_{u ∈ N(v)} W_2 x_u^{(t)})
"""

import numpy as np
from typing import Dict, List, Tuple, Callable
from kmath.core.state import KState
from kmath.core.operators import KNodeUpdateOperator


class GNNDynamics:
    """
    GNN-like message passing dynamics on a graph.
    
    Each node aggregates information from its neighbors via:
        x_v^{(t+1)} = σ(W_1 x_v^{(t)} + Σ_{u ∈ N(v)} W_2 x_u^{(t)})
    
    where:
    - σ is an activation function
    - W_1 is the self-weight matrix
    - W_2 is the neighbor-weight matrix
    """
    
    def __init__(
        self,
        W1: np.ndarray,
        W2: np.ndarray,
        activation: Callable[[np.ndarray], np.ndarray] = None
    ):
        """
        Initialize GNN dynamics.
        
        Args:
            W1: Self-weight matrix (d x d)
            W2: Neighbor-weight matrix (d x d)
            activation: Activation function σ. Default is ReLU.
        """
        self.W1 = np.array(W1)
        self.W2 = np.array(W2)
        
        if activation is None:
            self.activation = lambda x: np.maximum(0, x)  # ReLU
        else:
            self.activation = activation
        
        if self.W1.shape != self.W2.shape:
            raise ValueError("W1 and W2 must have the same shape")
        
        self.feature_dim = self.W1.shape[0]
    
    def create_graph_state(
        self,
        node_features: Dict[any, np.ndarray],
        edges: List[Tuple[any, any]]
    ) -> KState:
        """
        Create K-state from graph structure.
        
        Args:
            node_features: Dict mapping node IDs to feature vectors
            edges: List of (source, target) edge tuples
            
        Returns:
            K-state representation
        """
        # Convert edges to edge dict (we don't use edge features here, so use ones)
        edge_dict = {}
        for u, v in edges:
            edge_dict[(u, v)] = np.array([1.0])
        
        return KState(
            nodes=node_features,
            edges=edge_dict,
            labels={'gnn_graph'}
        )
    
    def get_operator(self) -> KNodeUpdateOperator:
        """
        Get a basic K-operator implementing self-transformation only.
        
        Note: This method only applies self-transformation without neighbor aggregation.
        For full GNN dynamics with neighbor aggregation, use `get_full_operator(state)`
        or `simulate(state, num_iterations)`.
        
        Returns:
            K-operator for self-transformation
        """
        def gnn_update(x_v, incident_edges, context):
            """
            GNN self-transformation (without neighbor aggregation).
            
            Args:
                x_v: Current node state
                incident_edges: Dict of incoming edges (not used in this basic version)
                context: Context vector (unused)
            """
            # Self-transformation only
            h = self.W1 @ x_v
            
            # Apply activation
            return self.activation(h)
        
        return KNodeUpdateOperator(gnn_update)
    
    def get_full_operator(self, state: KState) -> KNodeUpdateOperator:
        """
        Get operator with access to full state for neighbor aggregation.
        
        Args:
            state: Current state (to access neighbor features)
            
        Returns:
            K-operator for message passing
        """
        def gnn_update(x_v, incident_edges, context):
            # Self-transformation
            h = self.W1 @ x_v
            
            # Aggregate neighbor messages
            for (u, v), _ in incident_edges.items():
                if u in state.nodes:
                    h = h + self.W2 @ state.nodes[u]
            
            # Apply activation
            return self.activation(h)
        
        return KNodeUpdateOperator(gnn_update)
    
    def simulate(
        self,
        initial_state: KState,
        num_iterations: int
    ) -> List[KState]:
        """
        Simulate GNN dynamics for multiple iterations.
        
        Args:
            initial_state: Initial graph state
            num_iterations: Number of message-passing iterations
            
        Returns:
            List of states [s_0, s_1, ..., s_T]
        """
        trajectory = [initial_state]
        current_state = initial_state
        
        for _ in range(num_iterations):
            # Get operator with current state for neighbor access
            operator = self.get_full_operator(current_state)
            current_state = operator(current_state)
            trajectory.append(current_state)
        
        return trajectory
    
    def steady_state(
        self,
        initial_state: KState,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> KState:
        """
        Find steady state of GNN dynamics.
        
        Args:
            initial_state: Initial graph state
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            
        Returns:
            Steady state
        """
        current_state = initial_state
        
        for _ in range(max_iterations):
            operator = self.get_full_operator(current_state)
            next_state = operator(current_state)
            
            # Check convergence
            max_diff = 0.0
            for node_id in current_state.nodes:
                diff = np.linalg.norm(next_state.nodes[node_id] - current_state.nodes[node_id])
                max_diff = max(max_diff, diff)
            
            if max_diff < tolerance:
                return next_state
            
            current_state = next_state
        
        return current_state
