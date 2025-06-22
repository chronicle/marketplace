# Google SecOps Integrations Development

Welcome to the integration development documentation! This directory contains guides and resources to help you
understand, develop, and contribute integrations to the Google SecOps Marketplace Content Repository.

## Overview

Google SecOps SOAR (Security Orchestration, Automation, and Response) integrations enable you to connect with various
security tools and services, automate workflows, and enhance your security operations. This documentation provides
guidelines for creating, testing, and implementing these integrations.

## Public Documentation Resources

Before diving into development, we recommend familiarizing yourself with the official Google SecOps SOAR documentation:

- [Using the Google SecOps Marketplace](https://cloud.google.com/chronicle/docs/soar/marketplace/using-the-marketplace)
  —Learn how integrations are used in Google SecOps SOAR
- [Google Cloud Chronicle Documentation](https://cloud.google.com/chronicle/docs)—Comprehensive documentation about
  Google Cloud Chronicle

## Development Guides

This directory contains the following essential guides for integration development:

- [**Creating Integrations**](./creating_integrations.md)—Comprehensive step-by-step guide on how to develop, build,
  and package your own custom integrations for Google SecOps SOAR.

- [**Tests**](./tests.md)—Instructions for writing and running tests for your integrations to ensure they work as
  expected and maintain quality over time.

- [**Actions**](./actions.md)—Documentation about integration actions, their structure, implementation details, and
  best practices for creating effective actions.

- [**Examples**](./examples.md)—Code examples and use cases demonstrating how to implement various integration
  features and common patterns.

## Integration Structure

Each integration follows a standard structure within the repository. Understanding this structure is essential for
effective development:

- **definition.yaml** Defines the integration's metadata, version, and capabilities
- **pyproject.toml** Specifies the integration's Python dependencies
- **Directories**:
    - **actions/** Contains the integration's actions
    - **core/** Contains core functionality and helpers
    - **tests/** Contains test files for the integration

## Development Workflow

When developing integrations for Google SecOps SOAR, we recommend following this workflow:

1. Set up your development environment using the [Installation Guide](../installation_guide.md)
2. Follow the [Creating Integrations](./creating_integrations.md) guide to structure your integration
3. Use the MP CLI tool for building and validating your integration
4. Write comprehensive tests following the [Tests](./tests.md) guide
5. Run all tests locally before submitting a PR
6. Ensure your code follows our [Code Style Guide](../code_style.md)

## Quality Assurance

All integrations must pass our quality checks before being accepted:

- Linting and formatting checks using Ruff
- Type checking with Mypy
- Unit and integration tests
- Documentation completeness

These checks are enforced through GitHub Actions in the CI/CD pipeline.

## Additional Resources

For more information about development in this repository, refer to:

- [Development Documentation](../README.md) - General development resources and guidelines
- [Linters & Formatters](../linters_formatters.md)—Tools we use to enforce code quality
- [Main Repository README](../../../README.md) - High-level overview of the repository

## Contributing

We welcome contributions from the community! Before submitting your integration, please ensure you've followed all the
guidelines in this documentation and the [Contributing Guide](../../contributing.md).

If you have any questions or need assistance, please feel free to open an issue or reach out to the repository
maintainers.