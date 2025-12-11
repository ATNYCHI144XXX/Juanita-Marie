"""
Tests for K-operators.
"""

import numpy as np
import pytest
from kmath.core.state import KState
from kmath.core.operators import (
    KOperator,
    KNodeUpdateOperator,
    KEdgeUpdateOperator,
    KLabelOperator,
    KContextUpdateOperator,
    operator_add,
)


def test_koperator_basic():
    """Test basic K-operator functionality."""
    def double_nodes(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] * 2
        return new_state
    
    op = KOperator(double_nodes)
    
    nodes = {'a': np.array([1.0, 2.0])}
    state = KState(nodes, {})
    
    result = op(state)
    
    assert np.allclose(result.nodes['a'], np.array([2.0, 4.0]))


def test_koperator_composition():
    """Test operator composition."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    def multiply_two(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] * 2
        return new_state
    
    op1 = KOperator(add_one)
    op2 = KOperator(multiply_two)
    
    composed = op2.compose(op1)  # First add 1, then multiply by 2
    
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {})
    
    result = composed(state)
    
    # (1 + 1) * 2 = 4
    assert np.allclose(result.nodes['a'], np.array([4.0]))


def test_koperator_multiplication_syntax():
    """Test operator composition with * syntax."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    def multiply_two(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] * 2
        return new_state
    
    op1 = KOperator(add_one)
    op2 = KOperator(multiply_two)
    
    composed = op2 * op1
    
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {})
    
    result = composed(state)
    
    assert np.allclose(result.nodes['a'], np.array([4.0]))


def test_node_update_operator():
    """Test node update operator."""
    def update_func(x_v, incident_edges, context):
        # Simple: add 1 to each element
        return x_v + 1.0
    
    op = KNodeUpdateOperator(update_func)
    
    nodes = {'a': np.array([1.0, 2.0]), 'b': np.array([3.0, 4.0])}
    edges = {('a', 'b'): np.array([0.5])}
    state = KState(nodes, edges)
    
    result = op(state)
    
    assert np.allclose(result.nodes['a'], np.array([2.0, 3.0]))
    assert np.allclose(result.nodes['b'], np.array([4.0, 5.0]))


def test_edge_update_operator():
    """Test edge update operator."""
    def update_func(w_e, x_u, x_v, context):
        # Sum of endpoint states
        return np.array([np.sum(x_u) + np.sum(x_v)])
    
    op = KEdgeUpdateOperator(update_func)
    
    nodes = {'a': np.array([1.0]), 'b': np.array([2.0])}
    edges = {('a', 'b'): np.array([0.0])}
    state = KState(nodes, edges)
    
    result = op(state)
    
    assert np.allclose(result.edges[('a', 'b')], np.array([3.0]))


def test_label_operator():
    """Test label operator."""
    def update_func(labels, state):
        new_labels = labels.copy()
        if len(state.nodes) > 1:
            new_labels.add('multi_node')
        return new_labels
    
    op = KLabelOperator(update_func)
    
    nodes = {'a': np.array([1.0]), 'b': np.array([2.0])}
    state = KState(nodes, {}, {'initial'})
    
    result = op(state)
    
    assert 'initial' in result.labels
    assert 'multi_node' in result.labels


def test_context_update_operator():
    """Test context update operator."""
    def update_func(context, state):
        # Average of all node states
        total = 0.0
        count = 0
        for node_state in state.nodes.values():
            total += np.sum(node_state)
            count += len(node_state)
        return np.array([total / count if count > 0 else 0.0])
    
    op = KContextUpdateOperator(update_func)
    
    nodes = {'a': np.array([1.0, 3.0]), 'b': np.array([2.0, 4.0])}
    state = KState(nodes, {}, context=np.array([0.0]))
    
    result = op(state)
    
    # Average: (1 + 3 + 2 + 4) / 4 = 2.5
    assert np.allclose(result.context, np.array([2.5]))


def test_operator_add():
    """Test operator pointwise addition."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    def add_two(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 2
        return new_state
    
    op1 = KOperator(add_one)
    op2 = KOperator(add_two)
    
    sum_op = operator_add(op1, op2)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = sum_op(state)
    
    # (0 + 1) + (0 + 2) = 3
    assert np.allclose(result.nodes['a'], np.array([3.0]))
