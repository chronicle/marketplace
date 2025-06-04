# Google SecOps Marketplace Integration Guide

## Overview

The `mp` tool simplifies developing, testing, and maintaining integrations for the
Google SecOps Marketplace. This document explains the structure of marketplace
integrations and how to work with them using the tool.

## Integration Structure

A marketplace integration consists of:

1. **Metadata**: YAML files describing the integration, its capabilities, parameters,
   etc.
2. **Scripts**: Python code that implements the integration functionality
3. **Dependencies**: Required Python packages for the integration

Integrations exist in two states:

- **Non-built**: Source code format used during development
- **Built**: Packaged format ready for deployment to the marketplace

## Creating a New Integration

1. Create a directory for your integration in the appropriate repository (commercial or
   community)
2. Set up the required structure:

```
my_integration/
├── metadata/         # Metadata YAML files
│   ├── action.yaml   # Action definitions
│   ├── connector.yaml # Connector definitions
│   └── job.yaml      # Job definitions
├── scripts/          # Python implementation
│   ├── actions/      # Action implementations
│   ├── connectors/   # Connector implementations
│   └── jobs/         # Job implementations
├── tests/            # Test suite
└── pyproject.toml    # Python project configuration
```

## Building Integrations

To build your integration for deployment:

```bash
mp build --integration my_integration
```

This command:

1. Processes all metadata YAML files and converts them to JSON
2. Restructures scripts for deployment
3. Creates a deployable package in the output directory

## Deconstructing Built Integrations

To convert a built integration back to its non-built source form:

```bash
mp build --integration my_integration --deconstruct
```

This is useful when you have a built integration and want to make changes to it.

## Testing Integrations

The `mp` tool does not directly provide testing functionality for integrations, but you
can set up tests in the `tests/` directory of your integration and use standard Python
testing tools.

## Best Practices

1. **Metadata First**: Design your integration metadata carefully before implementing
   scripts
2. **Type Safety**: Use type hints in all your Python code
3. **Error Handling**: Implement robust error handling in your scripts
4. **Documentation**: Document your integration thoroughly
5. **Testing**: Create comprehensive tests for your integration
6. **Dependencies**: Keep dependencies minimal and pin versions

## Common Issues

### Import Restructuring

The tool automatically restructures imports in your scripts during the build process. Be
aware that:

- Relative imports may be converted to absolute imports
- Common packages might be handled differently in built vs. non-built modes

### Duplicate Integrations

The tool checks for duplicate integrations across repositories. Ensure your integration
name is unique.

### File Structure

Maintain the expected file structure for your integration to ensure proper building and
deconstructing.
