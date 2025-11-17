# Contributing to Thorlabs MDT Controller

Thank you for considering contributing to this project! We welcome contributions from the community.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

This project adheres to professional standards of conduct. Be respectful, constructive, and collaborative.

**Expected Behavior:**
- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## How Can I Contribute?

### 1. Report Bugs
See [Reporting Bugs](#reporting-bugs) section below.

### 2. Suggest Enhancements
Open an issue with the label `enhancement` describing your idea.

### 3. Write Code
- Fix bugs
- Implement new features
- Improve documentation
- Add tests

### 4. Improve Documentation
- Fix typos or unclear sections
- Add examples
- Write tutorials

---

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Windows OS (for hardware testing)

### Setup Steps

```powershell
# 1. Fork and clone your fork
git clone https://github.com/YOUR-USERNAME/Thorlabs_MDT.git
cd Thorlabs_MDT

# 2. Add upstream remote
git remote add upstream https://github.com/JovanMarkov96/Thorlabs_MDT.git

# 3. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install development tools (optional)
pip install black ruff pytest mypy

# 6. Create a feature branch
git checkout -b feature/my-feature
```

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these specifics:

- **Line length**: 100 characters (max 120 for long strings)
- **Indentation**: 4 spaces
- **Imports**: Standard library → Third-party → Local
- **Docstrings**: Google style
- **Type hints**: Required for public APIs

### Example

```python
#!/usr/bin/env python
# SPDX-License-Identifier: MIT
"""
Module docstring explaining purpose.

This module provides...
"""

import sys
from typing import Optional, Dict

import serial
from PyQt5.QtWidgets import QWidget


class MyClass:
    """
    Brief description of class.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    """
    
    def __init__(self, param1: str, param2: int = 10):
        self.param1 = param1
        self.param2 = param2
    
    def my_method(self, arg: float) -> Optional[str]:
        """
        Brief description of method.
        
        Args:
            arg: Description of arg
            
        Returns:
            Description of return value, or None if failure
        """
        # Implementation
        return None
```

### Code Quality Tools

```powershell
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/
```

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(controller): add voltage ramping function

fix(gui): prevent crash when device disconnected

docs(readme): update installation instructions
```

---

## Pull Request Process

### Before Submitting

1. **Update documentation** for any API changes
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Format code** with black/ruff
5. **Update CHANGELOG.md** with your changes
6. **Rebase on latest main**: `git pull upstream main --rebase`

### Submitting

1. **Push to your fork**:
   ```powershell
   git push origin feature/my-feature
   ```

2. **Create Pull Request** on GitHub

3. **PR Description Template**:
   ```markdown
   ## Description
   Brief summary of changes.
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   How was this tested?
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] CHANGELOG.md updated
   ```

### Review Process

- Maintainers will review within 1-2 weeks
- Address any requested changes
- Once approved, PR will be merged

---

## Reporting Bugs

### Before Reporting

1. **Check existing issues** for duplicates
2. **Test with latest version** from main branch
3. **Gather information** (OS, Python version, hardware)

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: Windows 10/11
- Python Version: 3.10.5
- Package Version: 0.1.0
- Device Model: MDT693A

## Additional Context
- Error messages/stack traces
- Screenshots
- Relevant code snippets
```

---

## Suggesting Enhancements

### Enhancement Proposal Template

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
What other approaches were considered?

## Additional Context
- Mockups/diagrams
- Code examples
- Related issues
```

---

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Mirror source structure: `tests/test_controller.py` for `src/mdt/controller.py`
- Use descriptive test names: `test_set_voltage_validates_range`
- Test edge cases and error conditions

### Example Test

```python
import pytest
from mdt import MDTController

def test_controller_validates_voltage_range():
    """Test that controller rejects out-of-range voltages."""
    controller = MDTController(port="MOCK", model="MDT693B")
    
    # Should reject negative voltage
    result = controller.set_voltage("X", -10.0)
    assert result is False
    
    # Should reject voltage above maximum
    result = controller.set_voltage("X", 200.0)
    assert result is False
    
    # Should accept valid voltage
    result = controller.set_voltage("X", 50.0)
    assert result is True
```

### Running Tests

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_controller.py

# Run with coverage
pytest --cov=src/mdt tests/

# Run with verbose output
pytest -v
```

---

## Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def set_voltage(self, axis: str, voltage: float, verify: bool = True) -> bool:
    """
    Set voltage for specified axis.
    
    This method sends a voltage command to the device and optionally
    verifies the setting by reading back the actual voltage.
    
    Args:
        axis: Axis name ("X", "Y", or "Z")
        voltage: Target voltage in volts (0.0 - 150.0)
        verify: Whether to verify by reading back (default: True)
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If axis is invalid
        SerialException: If communication fails
        
    Example:
        >>> controller.set_voltage("X", 25.5)
        True
    """
```

---

## Questions?

- **GitHub Discussions**: Ask questions
- **GitHub Issues**: For bugs and features
- **Email**: (if provided)

---

Thank you for contributing! 🙏
