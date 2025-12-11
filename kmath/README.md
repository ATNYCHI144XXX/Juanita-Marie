# K-Math: Recursive Mathematics Framework

K-Math is a recursive mathematics framework designed to model complex systems as iterated operator dynamics over structured state spaces.

## Overview

The K-Math framework provides a unified approach to modeling dynamical systems through:

- **K-States**: Structured states (x, λ, c) consisting of graph-based numerical data, labels, and context
- **K-Operators**: Functions that transform states, including structural, numerical, context, and meta operators
- **K-Programs**: Sequential compositions of operators
- **K-Recurrence**: Recursive dynamics with fixed-point and cycle detection

## Installation

```bash
pip install -r requirements.txt
```

## Core Concepts

### K-State

A K-state is a triple `(x, λ, c)` where:
- `x` is the physical/numerical state realized as a graph with nodes and edges
- `λ` is a finite label set (tags, types, roles)
- `c` is a control/context vector

```python
from kmath import KState
import numpy as np

state = KState(
    nodes={'v1': np.array([1.0, 2.0]), 'v2': np.array([3.0, 4.0])},
    edges={('v1', 'v2'): np.array([0.5])},
    labels={'graph', 'directed'},
    context=np.array([0.1, 0.2])
)
```

### K-Operators

K-operators transform states. There are four main types:

1. **Structural operators**: Modify labels and connectivity
2. **Numerical operators**: Act on numerical state and context
3. **Context operators**: Modify context without changing numerical state
4. **Meta operators**: Transform other operators

```python
from kmath import KNodeUpdateOperator
import numpy as np

# Define a node update function
def update_func(x_v, incident_edges, context):
    # Simple averaging with neighbors
    h = x_v.copy()
    for (u, v), weight in incident_edges.items():
        # Aggregate neighbor information
        h = h + 0.1 * weight[0]
    return h

operator = KNodeUpdateOperator(update_func)
new_state = operator(state)
```

### K-Programs

A K-program is a sequence of operators applied iteratively:

```python
from kmath import KProgram

program = KProgram([op1, op2, op3])

# Run for 10 iterations
final_state = program.run(initial_state, steps=10)

# Get full trajectory
trajectory = program.trajectory(initial_state, steps=10)
```

### K-Recurrence

Recursive dynamics with analysis capabilities:

```python
from kmath import KRecurrence

# Time-invariant recurrence
recurrence = KRecurrence(recurrence_map=operator)

# Find fixed points
fixed_point = recurrence.find_fixed_point(initial_state)

# Detect cycles
cycle = recurrence.find_cycle(initial_state)
```

## Examples

### Linear Time-Invariant (LTI) System

```python
from kmath.examples import LTISystem
import numpy as np

# Define system: x_{t+1} = A x_t + B u_t
A = np.array([[0.9, 0.1], [0.0, 0.8]])
B = np.array([[1.0], [0.5]])

lti = LTISystem(A, B)

# Simulate
x0 = np.array([1.0, 0.0])
control = np.ones((10, 1)) * 0.1
trajectory = lti.simulate(x0, control)

# Check stability
is_stable = lti.is_stable()
```

### Graph Neural Network Dynamics

```python
from kmath.examples import GNNDynamics
import numpy as np

# Define GNN weights
W1 = np.array([[0.5, 0.0], [0.0, 0.5]])  # Self-weight
W2 = np.array([[0.3, 0.0], [0.0, 0.3]])  # Neighbor-weight

gnn = GNNDynamics(W1, W2)

# Create graph
node_features = {
    'a': np.array([1.0, 0.0]),
    'b': np.array([0.0, 1.0]),
    'c': np.array([0.5, 0.5])
}
edges = [('a', 'b'), ('b', 'c'), ('c', 'a')]

initial_state = gnn.create_graph_state(node_features, edges)

# Simulate message passing
trajectory = gnn.simulate(initial_state, num_iterations=5)

# Find steady state
steady = gnn.steady_state(initial_state)
```

## Analysis Tools

### Fixed Point Detection

```python
from kmath.analysis import find_fixed_point

fixed_point = find_fixed_point(operator, initial_state, max_iterations=1000)
```

### Cycle Detection

```python
from kmath.analysis import find_cycle

cycle = find_cycle(operator, initial_state, max_iterations=1000)
```

### Stability Analysis

```python
from kmath.analysis import check_lyapunov_stability

is_stable = check_lyapunov_stability(operator, fixed_point)
```

## Operator Algebra

### Composition

```python
# (O2 ∘ O1)(s) = O2(O1(s))
composed = op2.compose(op1)
# Or using * syntax
composed = op2 * op1
```

### Addition

```python
from kmath.core.operators import operator_add

# (O1 ⊕ O2)(s) = O1(s) + O2(s)
sum_op = operator_add(op1, op2)
```

## Mathematical Foundations

The K-Math framework is based on the theory of recursive systems over structured state spaces. Key properties:

- **Composability**: Operators can be composed to form complex transformations
- **Recursion**: Systems evolve through iterated application of operators
- **Structure preservation**: Graph structure, labels, and context are maintained through transformations
- **Analysis**: Fixed points, cycles, and stability can be analyzed

## Documentation

For detailed mathematical background, see the whitepaper in `docs/KMATH_WHITEPAPER.md`.

## Testing

```bash
python -m pytest kmath/tests/
```

## License

See repository LICENSE file.

## Citation

If you use K-Math in your research, please cite:

```
@software{kmath2024,
  title={K-Math: Recursive Mathematics Framework},
  author={},
  year={2024},
  url={https://github.com/ATNYCHI144XXX/Juanita-Marie}
}
```
