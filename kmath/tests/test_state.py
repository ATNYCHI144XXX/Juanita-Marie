"""
Tests for KState class.
"""

import numpy as np
import pytest
from kmath.core.state import KState


def test_kstate_creation():
    """Test basic K-state creation."""
    nodes = {'a': np.array([1.0, 2.0]), 'b': np.array([3.0, 4.0])}
    edges = {('a', 'b'): np.array([0.5])}
    labels = {'test', 'graph'}
    context = np.array([0.1, 0.2])
    
    state = KState(nodes, edges, labels, context)
    
    assert 'a' in state.nodes
    assert 'b' in state.nodes
    assert ('a', 'b') in state.edges
    assert 'test' in state.labels
    assert 'graph' in state.labels
    assert np.allclose(state.context, context)


def test_kstate_copy():
    """Test K-state copying."""
    nodes = {'a': np.array([1.0, 2.0])}
    edges = {('a', 'a'): np.array([1.0])}
    state = KState(nodes, edges, {'label'})
    
    state_copy = state.copy()
    
    # Modify original
    state.nodes['a'][0] = 999.0
    
    # Copy should be unchanged
    assert state_copy.nodes['a'][0] == 1.0


def test_kstate_equality():
    """Test K-state equality comparison."""
    nodes1 = {'a': np.array([1.0, 2.0])}
    edges1 = {('a', 'a'): np.array([0.5])}
    state1 = KState(nodes1, edges1, {'label'}, np.array([0.1]))
    
    nodes2 = {'a': np.array([1.0, 2.0])}
    edges2 = {('a', 'a'): np.array([0.5])}
    state2 = KState(nodes2, edges2, {'label'}, np.array([0.1]))
    
    assert state1 == state2


def test_kstate_inequality():
    """Test K-state inequality."""
    nodes1 = {'a': np.array([1.0, 2.0])}
    state1 = KState(nodes1, {})
    
    nodes2 = {'a': np.array([1.0, 3.0])}
    state2 = KState(nodes2, {})
    
    assert state1 != state2


def test_kstate_no_context():
    """Test K-state without context."""
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {})
    
    assert state.context is None


def test_kstate_no_labels():
    """Test K-state without labels."""
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {})
    
    assert len(state.labels) == 0


def test_kstate_repr():
    """Test K-state string representation."""
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {}, {'label'}, np.array([0.1, 0.2]))
    
    repr_str = repr(state)
    assert 'KState' in repr_str
    assert 'nodes=1' in repr_str
    assert 'edges=0' in repr_str
