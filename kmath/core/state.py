"""
K-State: Structured state representation for K-Math framework.

A K-state is a triple (x, λ, c) where:
- x is the physical/numerical state (realized as a graph with nodes and edges)
- λ is a finite label set (tags, types, roles)
- c is a control/context vector
"""

from typing import Dict, Set, Optional, Tuple, Any
import numpy as np
import copy


class KState:
    """
    A K-state representing (x, λ, c).
    
    Attributes:
        nodes (Dict[Any, np.ndarray]): Mapping from node IDs to state vectors
        edges (Dict[Tuple[Any, Any], np.ndarray]): Mapping from edge IDs to weight vectors
        labels (Set[str]): Finite set of labels (tags, types, roles)
        context (Optional[np.ndarray]): Control/context vector
    """
    
    def __init__(
        self,
        nodes: Dict[Any, np.ndarray],
        edges: Dict[Tuple[Any, Any], np.ndarray],
        labels: Optional[Set[str]] = None,
        context: Optional[np.ndarray] = None
    ):
        """
        Initialize a K-state.
        
        Args:
            nodes: Dictionary mapping node IDs to state vectors (np.ndarray)
            edges: Dictionary mapping (source, target) tuples to edge weight vectors
            labels: Set of string labels (default: empty set)
            context: Context vector as np.ndarray (default: None)
        """
        self.nodes = {k: np.array(v) for k, v in nodes.items()}
        self.edges = {k: np.array(v) for k, v in edges.items()}
        self.labels = set(labels or [])
        self.context = np.array(context) if context is not None else None
    
    def copy(self) -> 'KState':
        """Create a deep copy of this state."""
        return KState(
            nodes=copy.deepcopy(self.nodes),
            edges=copy.deepcopy(self.edges),
            labels=copy.deepcopy(self.labels),
            context=copy.deepcopy(self.context)
        )
    
    def __eq__(self, other: 'KState') -> bool:
        """Check equality of two K-states."""
        if not isinstance(other, KState):
            return False
        
        # Check nodes
        if set(self.nodes.keys()) != set(other.nodes.keys()):
            return False
        for k in self.nodes:
            if not np.allclose(self.nodes[k], other.nodes[k]):
                return False
        
        # Check edges
        if set(self.edges.keys()) != set(other.edges.keys()):
            return False
        for k in self.edges:
            if not np.allclose(self.edges[k], other.edges[k]):
                return False
        
        # Check labels
        if self.labels != other.labels:
            return False
        
        # Check context
        if self.context is None and other.context is None:
            return True
        if self.context is None or other.context is None:
            return False
        return np.allclose(self.context, other.context)
    
    def __repr__(self) -> str:
        """String representation of K-state."""
        return (f"KState(nodes={len(self.nodes)}, edges={len(self.edges)}, "
                f"labels={self.labels}, context_dim={self.context.shape if self.context is not None else None})")
