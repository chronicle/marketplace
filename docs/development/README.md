# Development Documentation

Welcome to the development documentation section! This directory contains guides, standards, and resources to help you
understand and contribute to the Google SecOps Marketplace Content Repository effectively.

## Overview

This README serves as a legend to the documents in this directory, providing a brief description of each file and its
purpose. Use this guide to quickly find the information you need.

## General Development Resources

- [**Installation Guide**](./installation_guide.md)—Step-by-step instructions for setting up your development
  environment to work with this repository.

- [**Code Style**](./code_style.md)—Our coding standards and conventions for maintaining consistent and readable code
  across the project.

- [**Linters & Formatters**](./linters_formatters.md)—Information about the linting and formatting tools we use,
  including Ruff and Mypy, along with how to run checks with the `mp` CLI tool.

## Integration Development

The `integrations` subdirectory contains detailed guides for working with Google SecOps integrations:

- [**Creating Integrations**](./integrations/creating_integrations.md)—Comprehensive guide on how to develop, build, and
  package your own custom integrations for Google SecOps.

- [**Tests**](./integrations/tests.md)—Instructions for writing and running tests for your integrations to ensure they
  work as expected.

- [**Actions**](./integrations/actions.md)—Documentation about integration actions, their structure, and implementation
  details.

- [**Examples**](./integrations/examples.md)—Code examples and use cases that demonstrate how to implement various
  integration features.

## Tools and Utilities

Our repository includes several tools to help streamline development:

- **MP CLI Tool**—A command-line utility for building, testing, and validating integrations. The `mp check` and
  `mp format` commands are particularly useful for code quality assurance.

## Contribution Workflow

When contributing to this repository, we recommend the following workflow:

1. Set up your development environment using the Installation Guide
2. Familiarize yourself with our code standards
3. Use the provided linters and formatters to ensure code quality
4. Follow the specific guides for integration development if you're working on integrations
5. Run all tests locally before submitting a PR
6. Ensure all GitHub Actions pass on your PR

## Additional Resources

For more general information about the repository and contribution guidelines, refer to:

- [Main Repository README](../../README.md)
- [Contributing Guide](../contributing.md)
- [Core Concepts](../core_concepts.md)

## Need Help?

If you can't find what you're looking for or have questions, please feel free to open an issue or reach out to the
maintainers.