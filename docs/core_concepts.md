# Google SecOps Marketplace Content Repository Overview

This repository serves as the central hub for Google SecOps marketplace content, providing resources for connecting
Google SecOps with other security tools and platforms. It's designed to help users effectively use, develop, and
contribute to the Google SecOps ecosystem.

## Repository Structure

The repository is organized into several key directories:

### 1. Integrations

The `integrations/` directory contains various connectors that enable Google SecOps to interact with other security
products and services. Integrations are divided into two parts:

- `commercial` - Integrations developed by Google SecOps Marketplace developers
- `third_party` - Integrations developed by the community and our partners.

### 2. Documentation

The `docs/` directory houses comprehensive documentation:

- **Core concepts** Fundamental principles of Google SecOps integrations
- **Installation guides** Setup instructions for the repository
- **Development guides** Resources for creating and testing integrations
- **Code standards** Style guides and best practices

### 3. Packages

The `packages/` directory contains reusable libraries and packages:

- **TIPCommon** A shared library with multiple versions (1.0.10 through 2.0.6)
- **EnvironmentCommon** A support package with versions 1.0.1 and 1.0.2
- **mp** A CLI tool for building, testing, and quality assurance of integrations
- **integration_testing** A package that enables developers to test integrations in a "black box" manner and run scripts
  locally.

### 4. Tools

The `tools/` directory provides utility scripts and command-line tools to help with development tasks, including an
integration zipper for packaging.

## Development Environment

The project uses:

- Python 3.11
- `uv` for package management

## Community and Contribution

The repository is designed for community contributions with:

- Detailed contribution guidelines
- Code of conduct for maintaining a welcoming community
- Apache 2.0 licensing

## Current Status

The repository is marked as being in "Preview" status, with a warning that the structure might change in the future.
Currently, only community integrations are available in this repository.

This repository appears to be actively maintained, focusing on providing a robust ecosystem for integrating Google
SecOps with other security tools and platforms through a standardized framework.