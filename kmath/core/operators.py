"""
K-Operators: Functions that transform K-states.

A K-operator is a function O: S → S that transforms a K-state.
"""

from typing import Callable, Dict, Set, Tuple, Any
from kmath.core.state import KState
import numpy as np


class KOperator:
    """
    Base class for K-operators.
    
    A K-operator is a function O: S → S where S is the space of K-states.
    """
    
    def __init__(self, func: Callable[[KState], KState]):
        """
        Initialize a K-operator.
        
        Args:
            func: Function that maps KState → KState
        """
        self.func = func
    
    def __call__(self, state: KState) -> KState:
        """
        Apply the operator to a state.
        
        Args:
            state: Input K-state
            
        Returns:
            Transformed K-state
        """
        return self.func(state)
    
    def compose(self, other: 'KOperator') -> 'KOperator':
        """
        Compose this operator with another: (self ∘ other)(s) = self(other(s))
        
        Args:
            other: Another K-operator
            
        Returns:
            Composed operator
        """
        return KOperator(lambda s: self(other(s)))
    
    def __mul__(self, other: 'KOperator') -> 'KOperator':
        """Operator composition using * syntax."""
        return self.compose(other)


class KStructuralOperator(KOperator):
    """
    Structural operator: modifies labels and connectivity.
    
    Acts on the graph structure (nodes, edges, labels) without necessarily
    changing numerical values.
    """
    pass


class KNumericalOperator(KOperator):
    """
    Numerical operator: acts on x and possibly c.
    
    Modifies the numerical state of nodes and edges, and potentially the context.
    """
    pass


class KContextOperator(KOperator):
    """
    Context operator: modifies c without changing x.
    
    Updates the context vector while leaving node and edge states unchanged.
    """
    pass


class KMetaOperator(KOperator):
    """
    Meta operator: transforms other operators or operator sequences.
    
    Operates on the space of operators rather than directly on states.
    """
    
    def __init__(self, op_func: Callable[[KOperator], KOperator]):
        """
        Initialize a meta operator.
        
        Args:
            op_func: Function that transforms operators
        """
        self.op_func = op_func
        # Meta operators don't have a direct state function
        super().__init__(lambda s: s)
    
    def transform(self, operator: KOperator) -> KOperator:
        """
        Transform an operator.
        
        Args:
            operator: Operator to transform
            
        Returns:
            Transformed operator
        """
        return self.op_func(operator)


class KNodeUpdateOperator(KNumericalOperator):
    """
    Node update operator: updates node states based on local information.
    
    Updates each node's state based on:
    - Current node state
    - Incident edges
    - Context vector
    """
    
    def __init__(self, update_func: Callable[[np.ndarray, Dict[Tuple, np.ndarray], np.ndarray], np.ndarray]):
        """
        Initialize node update operator.
        
        Args:
            update_func: Function f(x_v, incident_edges, context) → new_x_v
                where incident_edges is a dict of {(u, v): edge_weight}
        """
        self.update_func = update_func
        
        def apply_to_state(state: KState) -> KState:
            new_state = state.copy()
            
            for node_id, node_state in state.nodes.items():
                # Gather incident edges
                incident_edges = {}
                for (u, v), edge_weight in state.edges.items():
                    if v == node_id:  # Incoming edge
                        incident_edges[(u, v)] = edge_weight
                
                # Update node
                new_state.nodes[node_id] = self.update_func(
                    node_state,
                    incident_edges,
                    state.context
                )
            
            return new_state
        
        super().__init__(apply_to_state)


class KEdgeUpdateOperator(KNumericalOperator):
    """
    Edge update operator: updates edge weights based on endpoint states.
    
    Updates each edge's weight based on:
    - Current edge weight
    - Source node state
    - Target node state
    - Context vector
    """
    
    def __init__(self, update_func: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray], np.ndarray]):
        """
        Initialize edge update operator.
        
        Args:
            update_func: Function g(w_e, x_u, x_v, context) → new_w_e
        """
        self.update_func = update_func
        
        def apply_to_state(state: KState) -> KState:
            new_state = state.copy()
            
            for (u, v), edge_weight in state.edges.items():
                x_u = state.nodes.get(u, np.zeros(1))
                x_v = state.nodes.get(v, np.zeros(1))
                
                new_state.edges[(u, v)] = self.update_func(
                    edge_weight,
                    x_u,
                    x_v,
                    state.context
                )
            
            return new_state
        
        super().__init__(apply_to_state)


class KLabelOperator(KStructuralOperator):
    """
    Label operator: updates label set based on state.
    
    Modifies the label set λ based on the current state.
    """
    
    def __init__(self, update_func: Callable[[Set[str], KState], Set[str]]):
        """
        Initialize label operator.
        
        Args:
            update_func: Function h(labels, state) → new_labels
        """
        self.update_func = update_func
        
        def apply_to_state(state: KState) -> KState:
            new_state = state.copy()
            new_state.labels = self.update_func(state.labels, state)
            return new_state
        
        super().__init__(apply_to_state)


class KContextUpdateOperator(KContextOperator):
    """
    Context update operator: updates context based on state.
    
    Modifies the context vector c based on the current state.
    """
    
    def __init__(self, update_func: Callable[[np.ndarray, KState], np.ndarray]):
        """
        Initialize context update operator.
        
        Args:
            update_func: Function q(context, state) → new_context
        """
        self.update_func = update_func
        
        def apply_to_state(state: KState) -> KState:
            new_state = state.copy()
            new_state.context = self.update_func(state.context, state)
            return new_state
        
        super().__init__(apply_to_state)


def operator_add(op1: KOperator, op2: KOperator) -> KOperator:
    """
    Pointwise addition of operators: (O1 ⊕ O2)(s) = O1(s) + O2(s).
    
    Note: This assumes the states can be added component-wise.
    
    Args:
        op1: First operator
        op2: Second operator
        
    Returns:
        Sum operator
    """
    def add_states(s1: KState, s2: KState) -> KState:
        """Add two states component-wise."""
        result = s1.copy()
        
        # Add node states
        for node_id in s1.nodes:
            if node_id in s2.nodes:
                result.nodes[node_id] = s1.nodes[node_id] + s2.nodes[node_id]
        
        # Add edge weights
        for edge_id in s1.edges:
            if edge_id in s2.edges:
                result.edges[edge_id] = s1.edges[edge_id] + s2.edges[edge_id]
        
        # Union labels
        result.labels = s1.labels | s2.labels
        
        # Add contexts
        if s1.context is not None and s2.context is not None:
            result.context = s1.context + s2.context
        
        return result
    
    return KOperator(lambda s: add_states(op1(s), op2(s)))
