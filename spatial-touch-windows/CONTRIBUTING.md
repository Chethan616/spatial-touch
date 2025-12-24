# Contributing to Spatial Touch

First off, thank you for considering contributing to Spatial Touch! 🎉

It's people like you that make Spatial Touch a great tool for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@spatialtouch.dev](mailto:conduct@spatialtouch.dev).

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Git
- Windows 10/11
- Webcam for testing

### Development Setup

```powershell
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/spatial-touch-windows.git
cd spatial-touch-windows

# 3. Add upstream remote
git remote add upstream https://github.com/spatial-touch/spatial-touch-windows.git

# 4. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 5. Install development dependencies
pip install -r requirements-dev.txt

# 6. Install pre-commit hooks
pre-commit install

# 7. Verify setup
pytest
```

### Project Structure Overview

```
spatial-touch-windows/
├── src/spatial_touch/     # Main source code
│   ├── core/              # Core modules
│   ├── utils/             # Utility functions
│   └── main.py            # Entry point
├── tests/                 # Test files
├── config/                # Configuration
├── docs/                  # Documentation
└── scripts/               # Build scripts
```

---

## 🔄 Development Workflow

### 1. Find an Issue

- Check [open issues](https://github.com/spatial-touch/spatial-touch-windows/issues)
- Look for `good first issue` or `help wanted` labels
- Comment on the issue to claim it

### 2. Create a Branch

```powershell
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/description` | `feature/scroll-gesture` |
| Bug Fix | `fix/description` | `fix/click-debounce` |
| Docs | `docs/description` | `docs/api-reference` |
| Refactor | `refactor/description` | `refactor/gesture-engine` |

### 3. Make Changes

- Write clean, documented code
- Follow our [style guidelines](#style-guidelines)
- Add tests for new functionality
- Update documentation as needed

### 4. Commit Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```powershell
# Format: <type>(<scope>): <description>

git commit -m "feat(gesture): add scroll gesture detection"
git commit -m "fix(camera): handle disconnect gracefully"
git commit -m "docs(readme): update installation steps"
git commit -m "test(engine): add pinch detection tests"
```

#### Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change, no feature/fix |
| `test` | Adding tests |
| `chore` | Build process, dependencies |

### 5. Push and Create PR

```powershell
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

---

## 🔀 Pull Request Process

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass (`pytest`)
- [ ] New code has test coverage
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] PR description is complete

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)

## Related Issues
Fixes #123
```

### Review Process

1. **Automated Checks** — CI runs tests, linting
2. **Code Review** — Maintainer reviews code
3. **Feedback** — Address any requested changes
4. **Approval** — Maintainer approves
5. **Merge** — Squash and merge to main

---

## 🎨 Style Guidelines

### Python Style

We use these tools to enforce consistent style:

```powershell
# Format code
black src tests

# Sort imports
isort src tests

# Check types
mypy src

# Lint
pylint src
flake8 src
```

### Code Style Rules

```python
# ✅ Good: Type hints, docstrings, clear naming
def calculate_distance(
    point_a: tuple[float, float, float],
    point_b: tuple[float, float, float]
) -> float:
    """Calculate Euclidean distance between two 3D points.
    
    Args:
        point_a: First point coordinates (x, y, z)
        point_b: Second point coordinates (x, y, z)
    
    Returns:
        Euclidean distance between the points
    
    Example:
        >>> calculate_distance((0, 0, 0), (1, 1, 1))
        1.732...
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


# ❌ Bad: No types, no docstring, unclear naming
def calc(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `GestureEngine` |
| Functions | snake_case | `detect_pinch` |
| Constants | UPPER_SNAKE | `MAX_HANDS` |
| Variables | snake_case | `frame_count` |
| Private | _leading | `_process_frame` |

### Documentation

```python
class GestureEngine:
    """Detects hand gestures from landmark data.
    
    The gesture engine processes hand landmarks from MediaPipe
    and detects predefined gestures like pinches, swipes, etc.
    
    Attributes:
        config: Gesture detection configuration
        state: Current gesture state machine state
    
    Example:
        >>> engine = GestureEngine(config)
        >>> gesture = engine.process(landmarks)
        >>> if gesture:
        ...     print(f"Detected: {gesture.type}")
    """
```

---

## 🧪 Testing

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src/spatial_touch --cov-report=html

# Run specific test file
pytest tests/test_gesture_engine.py

# Run specific test
pytest tests/test_gesture_engine.py::test_pinch_detection

# Run with verbose output
pytest -v
```

### Writing Tests

```python
# tests/test_gesture_engine.py

import pytest
from spatial_touch.core.gesture_engine import GestureEngine, GestureType

class TestPinchDetection:
    """Tests for pinch gesture detection."""
    
    @pytest.fixture
    def engine(self):
        """Create a gesture engine with default config."""
        return GestureEngine()
    
    def test_pinch_detected_when_fingers_close(self, engine):
        """Pinch should be detected when thumb and index are close."""
        # Arrange
        landmarks = create_mock_landmarks(thumb_index_distance=0.03)
        
        # Act
        gesture = engine.process(landmarks)
        
        # Assert
        assert gesture is not None
        assert gesture.type == GestureType.PINCH
    
    def test_no_pinch_when_fingers_far(self, engine):
        """No pinch when thumb and index are far apart."""
        landmarks = create_mock_landmarks(thumb_index_distance=0.15)
        
        gesture = engine.process(landmarks)
        
        assert gesture is None
    
    @pytest.mark.parametrize("distance,expected", [
        (0.01, True),
        (0.05, False),
        (0.10, False),
    ])
    def test_pinch_threshold(self, engine, distance, expected):
        """Test pinch detection at various distances."""
        landmarks = create_mock_landmarks(thumb_index_distance=distance)
        gesture = engine.process(landmarks)
        assert (gesture is not None) == expected
```

### Test Coverage Requirements

- New features: 80% minimum coverage
- Bug fixes: Test case for the fixed bug
- Core modules: 90% minimum coverage

---

## 📚 Documentation

### Updating Documentation

- **Code comments**: Explain *why*, not *what*
- **Docstrings**: All public functions/classes
- **README**: Update if adding features
- **Changelog**: Add entry for changes

### Changelog Format

```markdown
## [Unreleased]

### Added
- Scroll gesture support (#123)

### Changed
- Improved pinch detection accuracy (#124)

### Fixed
- Camera disconnect crash (#125)

### Deprecated
- Old configuration format (use settings.json)
```

---

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `feature` | New feature request |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `documentation` | Documentation improvements |
| `performance` | Performance improvements |
| `question` | Further information requested |

---

## 🎖️ Recognition

Contributors are recognized in:

- README.md Contributors section
- Release notes
- Annual contributor spotlight

---

## ❓ Questions?

- **Discord**: [Join our server](https://discord.gg/spatialtouch)
- **Discussions**: [GitHub Discussions](https://github.com/spatial-touch/spatial-touch-windows/discussions)
- **Email**: [contributors@spatialtouch.dev](mailto:contributors@spatialtouch.dev)

---

<div align="center">

**Thank you for contributing! 🙏**

Every contribution, no matter how small, makes a difference.

</div>
