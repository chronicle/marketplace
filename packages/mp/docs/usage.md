# Usage Guide

`mp` is a command-line tool for working with Google SecOps Marketplace integrations.
Below are the main commands and their usage.

## Basic Commands

### Getting Help

To see all available commands and general help:

```bash
mp --help
```

To get help for a specific command:

```bash
mp <command> --help
```

## Code Quality Commands

### Format Code

To format Python files in your project:

```bash
mp format [FILE_PATHS...]
```

Options:

- `--changed-files`: Format only files changed in Git
- `--quiet`: Reduce output verbosity
- `--verbose`: Increase output verbosity

### Lint and Check Code

To lint and check Python files:

```bash
mp check [FILE_PATHS...]
```

Options:

- `--fix`: Automatically fix minor issues
- `--changed-files`: Check only files changed in Git
- `--static-type-check`: Run static type checking with mypy
- `--raise-error-on-violations`: Raise error if violations are found
- `--quiet`: Reduce output verbosity
- `--verbose`: Increase output verbosity

## Integration Build Commands

### Building Integrations

To build integrations for Google SecOps Marketplace:

```bash
mp build
```

You must specify one of the following options:

- `--repository [REPOSITORY_TYPES...]`: Build all integrations in specified repositories
- `--integration [INTEGRATION_NAMES...]`: Build specific integration(s)
- `--group [GROUP_NAMES...]`: Build all integrations in specified group(s)

Additional options:

- `--deconstruct`: Deconstruct built integrations instead of building them (works only
  with `--integration`)
- `--quiet`: Reduce output verbosity
- `--verbose`: Increase output verbosity

## Examples

### Format Changed Files

```bash
mp format --changed-files
```

### Check and Fix a Specific File

```bash
mp check src/mp/core/utils.py --fix
```

### Build a Specific Integration

```bash
mp build --integration my_integration
```

### Build All Integrations in Commercial Repository

```bash
mp build --repository COMMERCIAL
```

### Deconstruct a Built Integration

```bash
mp build --integration my_integration --deconstruct
```
