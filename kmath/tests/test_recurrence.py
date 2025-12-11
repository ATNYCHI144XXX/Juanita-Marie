"""
Tests for K-recurrence.
"""

import numpy as np
import pytest
from kmath.core.state import KState
from kmath.core.operators import KOperator
from kmath.core.program import KProgram
from kmath.core.recurrence import KRecurrence


def test_krecurrence_time_invariant():
    """Test time-invariant recurrence."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = recurrence.iterate(state, steps=5)
    
    assert np.allclose(result.nodes['a'], np.array([5.0]))


def test_krecurrence_time_variant():
    """Test time-variant recurrence."""
    def add_time(state: KState, t: int) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + t
        return new_state
    
    recurrence = KRecurrence(time_variant_map=add_time)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = recurrence.iterate(state, steps=5)
    
    # Sum of 0 + 1 + 2 + 3 + 4 = 10
    assert np.allclose(result.nodes['a'], np.array([10.0]))


def test_krecurrence_trajectory():
    """Test trajectory generation."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    trajectory = recurrence.trajectory(state, steps=3)
    
    assert len(trajectory) == 4
    assert np.allclose(trajectory[0].nodes['a'], np.array([0.0]))
    assert np.allclose(trajectory[3].nodes['a'], np.array([3.0]))


def test_find_fixed_point():
    """Test fixed point detection."""
    def converge_to_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            x = new_state.nodes[node_id]
            # Converges to 1: x' = 0.5*x + 0.5
            new_state.nodes[node_id] = 0.5 * x + 0.5
        return new_state
    
    op = KOperator(converge_to_one)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    fixed_point = recurrence.find_fixed_point(state, max_iterations=100, tolerance=1e-6)
    
    assert fixed_point is not None
    assert np.allclose(fixed_point.nodes['a'], np.array([1.0]), atol=1e-5)


def test_find_fixed_point_not_found():
    """Test when fixed point is not found."""
    def diverge(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(diverge)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    fixed_point = recurrence.find_fixed_point(state, max_iterations=10, tolerance=1e-6)
    
    assert fixed_point is None


def test_find_cycle():
    """Test cycle detection."""
    def cycle_operator(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            x = new_state.nodes[node_id][0]
            # Cycle: 0 -> 1 -> 2 -> 0
            new_state.nodes[node_id] = np.array([(x + 1) % 3])
        return new_state
    
    op = KOperator(cycle_operator)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    cycle = recurrence.find_cycle(state, max_iterations=100, tolerance=0.1)
    
    assert cycle is not None
    assert len(cycle) == 3  # Cycle length should be 3


def test_from_program():
    """Test creating recurrence from program."""
    def add_one(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            new_state.nodes[node_id] = new_state.nodes[node_id] + 1
        return new_state
    
    op = KOperator(add_one)
    program = KProgram([op, op])
    
    recurrence = KRecurrence.from_program(program)
    
    nodes = {'a': np.array([0.0])}
    state = KState(nodes, {})
    
    result = recurrence.iterate(state, steps=2)
    
    # Each iteration applies the program (which adds 2)
    # 2 iterations: 0 + 2 + 2 = 4
    assert np.allclose(result.nodes['a'], np.array([4.0]))


def test_krecurrence_invalid():
    """Test that creating recurrence with both or neither map raises error."""
    with pytest.raises(ValueError):
        KRecurrence()
    
    op = KOperator(lambda s: s)
    with pytest.raises(ValueError):
        KRecurrence(recurrence_map=op, time_variant_map=lambda s, t: s)
