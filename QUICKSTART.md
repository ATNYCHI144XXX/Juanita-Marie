# K-Math Core Engine - Quick Start Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ATNYCHI144XXX/Juanita-Marie.git
cd Juanita-Marie
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -m pytest kmath/tests/
```

## Quick Start

### Basic Example

```python
import numpy as np
from kmath import KState, KOperator, KProgram

# Create a state
nodes = {'a': np.array([1.0, 2.0])}
state = KState(nodes, {})

# Create an operator
def double(s):
    new_s = s.copy()
    for node_id in new_s.nodes:
        new_s.nodes[node_id] *= 2
    return new_s

op = KOperator(double)

# Apply operator
result = op(state)
print(result.nodes['a'])  # [2.0, 4.0]
```

### LTI System Example

```python
from kmath.examples import LTISystem
import numpy as np

# Define system matrices
A = np.array([[0.9, 0.1], [0.0, 0.8]])
B = np.array([[1.0], [0.5]])

lti = LTISystem(A, B)

# Simulate
x0 = np.array([1.0, 0.0])
control = np.ones((10, 1)) * 0.1
trajectory = lti.simulate(x0, control)

print(f"Stable: {lti.is_stable()}")
```

### Fixed Point Detection

```python
from kmath import KRecurrence, KOperator, KState
import numpy as np

def converge(state):
    new_state = state.copy()
    for node_id in new_state.nodes:
        x = new_state.nodes[node_id]
        new_state.nodes[node_id] = 0.5 * x + 0.5
    return new_state

op = KOperator(converge)
rec = KRecurrence(recurrence_map=op)

state = KState({'x': np.array([0.0])}, {})
fixed = rec.find_fixed_point(state)

print(f"Fixed point: {fixed.nodes['x']}")  # ~[1.0]
```

## Running Examples

Run the comprehensive demo:
```bash
python examples_demo.py
```

## Documentation

- **Framework Overview**: `kmath/README.md`
- **Theoretical Background**: `docs/KMATH_WHITEPAPER.md`
- **API Documentation**: See docstrings in source files

## Project Structure

```
kmath/
├── core/              # Core framework components
│   ├── state.py       # KState class
│   ├── operators.py   # KOperator and subclasses
│   ├── program.py     # KProgram class
│   └── recurrence.py  # KRecurrence class
├── analysis/          # Analysis utilities
│   ├── fixed_points.py
│   └── stability.py
├── examples/          # Example embeddings
│   ├── lti_system.py
│   └── gnn_dynamics.py
└── tests/             # Test suite
```

## Key Concepts

### K-State
A triple `(x, λ, c)` representing:
- `x`: Graph-based numerical state (nodes + edges)
- `λ`: Label set
- `c`: Context vector

### K-Operator
A function `O: S → S` transforming states. Types:
- **Structural**: Modify graph/labels
- **Numerical**: Update values
- **Context**: Update context
- **Meta**: Transform operators

### K-Program
A sequence of operators applied iteratively.

### K-Recurrence
Recursive dynamics: `s_{t+1} = R(s_t)`

## Testing

Run all tests:
```bash
python -m pytest kmath/tests/ -v
```

Run specific test file:
```bash
python -m pytest kmath/tests/test_state.py -v
```

## Contributing

See repository contribution guidelines.

## License

See repository LICENSE file.

## Support

For issues or questions, please open an issue on GitHub.
