"""
Example script demonstrating K-Math framework usage.
"""

import numpy as np
from kmath import KState, KNodeUpdateOperator, KProgram, KRecurrence
from kmath.examples import LTISystem, GNNDynamics


def example_basic_operators():
    """Demonstrate basic operator usage."""
    print("=== Basic Operators Example ===")
    
    # Create a simple graph state
    nodes = {
        'a': np.array([1.0, 2.0]),
        'b': np.array([3.0, 4.0]),
        'c': np.array([5.0, 6.0])
    }
    edges = {
        ('a', 'b'): np.array([0.5]),
        ('b', 'c'): np.array([0.8]),
        ('c', 'a'): np.array([0.3])
    }
    
    state = KState(nodes, edges, labels={'graph'}, context=np.array([0.1]))
    
    print(f"Initial state: {state}")
    print(f"Node 'a': {state.nodes['a']}")
    
    # Define a simple node update operator
    def smooth_operator(x_v, incident_edges, context):
        """Average node state with neighbors."""
        result = x_v.copy()
        count = 1
        for (u, v), weight in incident_edges.items():
            # In this simplified version, we just use the weight
            result = result + weight[0]
            count += 1
        return result / count
    
    op = KNodeUpdateOperator(smooth_operator)
    new_state = op(state)
    
    print(f"After operator: Node 'a' = {new_state.nodes['a']}")
    print()


def example_lti_system():
    """Demonstrate LTI system embedding."""
    print("=== LTI System Example ===")
    
    # Define a stable 2D system
    A = np.array([[0.9, 0.1], [0.0, 0.8]])
    B = np.array([[1.0], [0.5]])
    
    lti = LTISystem(A, B)
    
    print(f"System is stable: {lti.is_stable()}")
    print(f"Eigenvalues: {lti.compute_eigenvalues()}")
    
    # Simulate with constant control
    x0 = np.array([1.0, 0.0])
    control_sequence = np.ones((10, 1)) * 0.1
    
    trajectory = lti.simulate(x0, control_sequence)
    
    print(f"Initial state: {trajectory[0]}")
    print(f"Final state: {trajectory[-1]}")
    print()


def example_gnn_dynamics():
    """Demonstrate GNN-like message passing."""
    print("=== GNN Dynamics Example ===")
    
    # Define GNN parameters
    W1 = np.array([[0.5, 0.0], [0.0, 0.5]])  # Self-weight
    W2 = np.array([[0.2, 0.0], [0.0, 0.2]])  # Neighbor-weight
    
    gnn = GNNDynamics(W1, W2)
    
    # Create a simple triangle graph
    node_features = {
        'a': np.array([1.0, 0.0]),
        'b': np.array([0.0, 1.0]),
        'c': np.array([0.5, 0.5])
    }
    edges = [('a', 'b'), ('b', 'c'), ('c', 'a')]
    
    initial_state = gnn.create_graph_state(node_features, edges)
    
    print(f"Initial features:")
    for node_id, features in initial_state.nodes.items():
        print(f"  {node_id}: {features}")
    
    # Run message passing
    trajectory = gnn.simulate(initial_state, num_iterations=3)
    
    print(f"\nAfter 3 iterations:")
    for node_id, features in trajectory[-1].nodes.items():
        print(f"  {node_id}: {features}")
    print()


def example_fixed_points():
    """Demonstrate fixed point detection."""
    print("=== Fixed Point Detection Example ===")
    
    # Create an operator that converges to a fixed point
    from kmath import KOperator
    
    def converge_op(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            x = new_state.nodes[node_id]
            # Converges to [1.0, 1.0]: x' = 0.8*x + 0.2
            new_state.nodes[node_id] = 0.8 * x + 0.2
        return new_state
    
    op = KOperator(converge_op)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'x': np.array([0.0, 0.0])}
    initial_state = KState(nodes, {})
    
    print(f"Initial state: {initial_state.nodes['x']}")
    
    fixed_point = recurrence.find_fixed_point(initial_state, max_iterations=100)
    
    if fixed_point:
        print(f"Fixed point found: {fixed_point.nodes['x']}")
        print(f"Expected: [1.0, 1.0]")
    print()


def example_cycle_detection():
    """Demonstrate cycle detection."""
    print("=== Cycle Detection Example ===")
    
    from kmath import KOperator
    
    def cycle_op(state: KState) -> KState:
        new_state = state.copy()
        for node_id in new_state.nodes:
            x = new_state.nodes[node_id][0]
            # Cycle: 0 -> 1 -> 2 -> 0
            new_state.nodes[node_id] = np.array([(x + 1) % 3])
        return new_state
    
    op = KOperator(cycle_op)
    recurrence = KRecurrence(recurrence_map=op)
    
    nodes = {'x': np.array([0.0])}
    initial_state = KState(nodes, {})
    
    print(f"Initial state: {initial_state.nodes['x'][0]}")
    
    cycle = recurrence.find_cycle(initial_state, max_iterations=100, tolerance=0.1)
    
    if cycle:
        print(f"Cycle detected with length: {len(cycle)}")
        print("Cycle states:")
        for i, state in enumerate(cycle):
            print(f"  State {i}: {state.nodes['x'][0]}")
    print()


if __name__ == "__main__":
    example_basic_operators()
    example_lti_system()
    example_gnn_dynamics()
    example_fixed_points()
    example_cycle_detection()
    
    print("=== All examples completed successfully! ===")
