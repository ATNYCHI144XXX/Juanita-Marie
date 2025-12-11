"""
Tests for K-programs.
"""

import numpy as np
import pytest
from kmath.core.state import KState
from kmath.core.operators import KOperator
from kmath.core.program import KProgram


def test_kprogram_creation():
    """Test K-program creation."""
    def identity(state):
        return state.copy()
    
    op = KOperator(identity)
    program = KProgram([op, op, op])
    
    assert len(program) == 3


def test_kprogram_step():
    """Test single program step."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    program = KProgram([op, op])
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = program.step(state)
    
    # Two applications: 0 + 1 + 1 = 2
    assert np.allclose(result.nodes['a'], np.array([2.0]))


def test_kprogram_run():
    """Test multiple program iterations."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    program = KProgram([op])
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = program.run(state, steps=5)
    
    # 5 iterations: 0 + 5 = 5
    assert np.allclose(result.nodes['a'], np.array([5.0]))


def test_kprogram_trajectory():
    """Test trajectory generation."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    program = KProgram([op])
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    trajectory = program.trajectory(state, steps=3)
    
    assert len(trajectory) == 4  # Initial + 3 steps
    assert np.allclose(trajectory[0].nodes['a'], np.array([0.0]))
    assert np.allclose(trajectory[1].nodes['a'], np.array([1.0]))
    assert np.allclose(trajectory[2].nodes['a'], np.array([2.0]))
    assert np.allclose(trajectory[3].nodes['a'], np.array([3.0]))


def test_kprogram_empty():
    """Test empty program."""
    program = KProgram([])
    
    nodes = {'a': np.array([1.0])}
    state = KState(nodes, {})
    
    result = program.step(state)
    
    # No operators, state unchanged
    assert np.allclose(result.nodes['a'], np.array([1.0]))


def test_kprogram_complex():
    """Test complex multi-operator program."""
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
    
    program = KProgram([op1, op2, op1])
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = program.step(state)
    
    # ((0 + 1) * 2) + 1 = 3
    assert np.allclose(result.nodes['a'], np.array([3.0]))
