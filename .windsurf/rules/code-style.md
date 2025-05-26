---
trigger: model_decision
description: When writing python code please adhere to the following rules
---

- The code should be written following the coding standards enforced by `ruff`
- Use the `uv` tool for managing dependencies
- Code should be written following `SOLID` principles
- ALL python code must include type hints
- Create docstrings for ALL public methods
- Private methods should have self documenting names
- Testing will leverage the `pytest` package