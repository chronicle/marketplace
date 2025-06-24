# Code Style Guide

This document outlines the coding standards and style guidelines for the Google SecOps Marketplace Content Repository.
Following these guidelines ensures consistency, readability, and maintainability across the codebase.

## General Principles

- **Consistency**: Code should look as if it was written by a single person, even when multiple contributors are
  involved.
- **Readability**: Code should be easy to understand for both current and future developers.
- **Simplicity**: Prefer simple, straightforward solutions over complex ones.
- **Maintainability**: Write code that can be easily maintained and extended.

## Python Style Guidelines

### Google Python Style Guide

We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) as our primary reference for
Python code style. This comprehensive guide covers everything from code layout to documentation standards. Familiarize
yourself with this guide to understand our coding conventions in detail.

### Type Annotations

All Python code in this repository must use type hints. Type annotations improve code readability, enable better tooling
support, and help catch type-related errors early.

#### Future Annotations

Every Python file in the repository **must** include the following import at the top:

```python
from __future__ import annotations
```

This import allows you to use forward references in type annotations without quotes, which improves readability and
maintainability. It's especially important until we fully migrate to Python 3.14, which will make this behavior the
default.

For example, with this import you can write:

```python
from __future__ import annotations


class Tree:
    def get_child(self) -> Tree:  # No quotes needed around 'Tree'
        ...
```

Instead of:

```python
class Tree:
    def get_child(self) -> 'Tree':  # Quotes required without the import
        ...
```

#### TYPE_CHECKING for Import Cycles

Use `TYPE_CHECKING` to avoid import cycles that can occur due to type annotations. This is especially useful when you
have circular dependencies between modules:

```python
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterable  # Only imported during type checking


def process_data(input_data: dict[str, Iterable[int]], max_items: int = 100) -> list[str]:
    """Process the input data and return a list of strings.

    Args:
        input_data: A dictionary containing the data to process.
        max_items: Maximum number of items to process.

    Returns:
        A list of processed string items.

    """
    ...
```

The `TYPE_CHECKING` constant is `False` at runtime but `True` during type checking, so imports inside this block won't
cause circular import errors at runtime.

#### Example of Proper Type Annotation

```python
from __future__ import annotations

from typing import Any


def process_data(input_data: dict[str, Any], max_items: int = 100) -> list[str]:
    """Process the input data and return a list of strings.

    Args:
        input_data: A dictionary containing the data to process.
        max_items: Maximum number of items to process.

    Returns:
        A list of processed string items.

    """
    ...
```

For complex types, consider using type aliases or creating custom types using `TypedDict`, `NamedTuple`, or similar
constructs from the `typing` module.

#### Generic vs. Specific Type Annotations

When designing functions and methods, follow these guidelines for type annotations:

1. **Use generic types in parameter signatures**:
    - Accept the most general type that your function can handle
    - This allows for flexibility and reusability
    - Use protocol classes or ABC interfaces when appropriate

2. **Return specific types in return annotations**:
    - Be as specific as possible about what your function returns
    - This helps callers understand exactly what they're getting
    - Avoid returning `Any` whenever possible

Example of the following pattern:

```python
from __future__ import annotations

import dataclasses
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
   from collections.abc import Iterable, Mapping


@dataclasses.dataclass
class User:
   ...


# Generic Mapping in, specific list[User] out
def process_users(user_data: Mapping[str, Any]) -> list[User]:
   """Process user data and return a list of User objects.

   Args:
       user_data: Any mapping containing user information.

   Returns:
       A list of fully initialized User objects.
   """
   result = []
   for user_id, data in user_data.items():
      result.append(User(id=user_id, **data))
   return result


# Generic Iterable in, specific list out
def filter_active(items: Iterable[User]) -> list[User]:
   """Filter and return only active users.

   Args:
       items: Any iterable containing User objects.

   Returns:
       A list containing only the active users.
   """
   return [item for item in items if item.is_active]
```

This approach maximizes code flexibility while maintaining type safety and clarity.

### Docstrings

All public modules, functions, classes, and methods should have docstrings that follow the Google style docstring
format:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    More detailed explanation of the function's purpose and behavior.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When and why this exception is raised.

    """
    ...
```

### Code Formatting

#### Line Length

The maximum line length is 88 characters, the same as the Black formatter's default.

#### Indentation

Use four spaces for indentation. Do not use tabs.

#### Imports

Imports should be grouped in the following order, with a blank line between each group:

1. Standard library imports
2. Related third-party imports
3. Local application/library specific imports

Within each group, imports should be sorted alphabetically.

## Code Quality Tools

### Ruff

We use Ruff as our primary linter and formatter. Ruff combines the functionality of multiple Python linters and provides
fast, consistent code formatting.

To format your code with Ruff, use the `mp format` command:

```bash
mp format path/to/files
```

To check for linting issues:

```bash
mp check [options]
```

To automatically fix linting issues where possible:

```bash
mp check --fix
```

### Mypy

We use Mypy for static type checking. Mypy helps ensure that type annotations are correct and consistent throughout the
codebase.

Mypy checks can be run as part of the `mp check` command with the `--static-type-check` flag:

```bash
mp check --static-type-check
```

## Pre-Commit Workflow

Before submitting a pull request, always:

1. Format your code with `mp format`
2. Run linting checks with `mp check`
3. Ensure type checking passes with `mp check --static-type-check`
4. Fix any issues identified by these tools

## GitHub Actions

All pull requests are automatically checked using GitHub Actions to ensure they meet our code style guidelines. The CI
pipeline runs the same checks you should run locally before submitting your PR.

Pull requests with failing checks will not be merged until all issues are resolved.

## Additional Best Practices

### Class Design

- Follow object-oriented design principles
- Use descriptive class and method names
- Make proper use of inheritance and composition

### Error Handling

- Use specific exception types instead of generic exceptions
- Handle exceptions at the appropriate level
- Provide clear error messages

### Comments

- Write comments that explain "why" rather than "what"
- Keep comments up to date with code changes
- Use comments sparingly—prefer self-documenting code when possible

### Variable Naming

- Use descriptive variable names that indicate purpose
- Follow naming conventions (snake_case for variables and functions, PascalCase for classes)
- Avoid single-letter variable names except in specific contexts (e.g., loop indices)

## Conclusion

Following these code style guidelines helps maintain a high-quality, consistent codebase that is straightforward to
understand and
modify. If you have questions about a specific style guideline not covered here, refer to the Google Python Style Guide
or ask for clarification from the repository maintainers.