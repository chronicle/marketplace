# Linters and Formatters

This page describes the code quality tools used in this repository to ensure consistent code style and catch potential
issues.

## Ruff

Ruff is the primary code linter and formatter used in this project. It's a fast Python linter written in Rust that helps
identify various code issues.

### Configuration

Ruff is configured through `ruff.toml` files that are located in each sub-project. These files determine the code
validations specific to each part of the codebase. The configuration includes:

- Line length (88 characters, same as Black)
- Target Python version (3.11)
- Various rule selections and ignores
- Special handling for test files
- Custom format settings

## MP Commands

The repository uses custom `mp` commands to handle linting and formatting:

### MP Check

The `mp check` is a wrapper around ruff that runs linting checks on the codebase. It can detect various issues and code
style violations.

Usage:

```bash
mp check [options]  # Basic check
mp check --fix      # Automatically fix violations where possible
```

The command supports various output formats, including:

- concise
- full
- json
- json-lines
- junit
- grouped
- github
- gitlab
- pylint
- rdjson
- azure
- sarif

See more at the [documentation of mp](/packages/mp/README.md)

### MP Format

The `mp format` command automatically formats code according to the project's style guidelines.

Usage:

```bash
mp format path/to/files
```

See more at the [documentation of mp](/packages/mp/README.md)

## Mypy

Mypy is used for static type checking in Python. It helps catch type-related errors before runtime.

The project uses mypy to validate type hints throughout the codebase, ensuring type safety and better code
documentation.

Mypy can be run as part of `mp check` when using the `--static-type-check` flag.

## GitHub Actions

All linting and formatting checks are enforced through GitHub Actions in the CI/CD pipeline. For every pull request, the
following checks are run:

- Code linting and formatting validation
- Type checking
- Various tests

All GitHub Actions are expected to pass for each PR before it can be merged. The main workflow for code quality is
defined in `.github/workflows/code_checks.yml`, which runs the `mp check` command on changed files.

## Best Practices

1. Run `mp check` and `mp format` locally before submitting a PR
2. Address all linting issues identified by the tools
3. Ensure mypy type checking passes without errors
4. Make sure all GitHub Actions pass before requesting a code review

By following these guidelines, we maintain high code quality standards throughout the project.