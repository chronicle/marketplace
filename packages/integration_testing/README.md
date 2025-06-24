# mp: Your Google SecOps Marketplace Integration Powerhouse

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
![Maintenance](https://img.shields.io/maintenance/yes/2025)

**`mp`**, short for **`google_secops_marketplace`**, is a command-line interface (CLI)
tool designed to streamline the development and maintenance of Google SecOps marketplace
integrations. It empowers developers by providing a unified platform for building,
testing, and ensuring the quality of their integrations.

## Key Features

* **Effortless Integration Building:** Simplify the creation of new Google SecOps
  integrations with intuitive commands and project scaffolding.
* **Automated Code Checks:** Ensure code quality and adherence to best practices through
  integrated code analysis.
* **Linting and Formatting:** Automatically identify and fix stylistic issues,
  maintaining a consistent and readable codebase.
* **Testing Capabilities:** Run unit tests and initiate black box tests to validate the
  functionality and reliability of your integrations.

## Getting Started

### Installation

First, change your current directory to the directory of the integration you want to support integration_testing

```bash
cd /path/to/integration
```

Then, if you haven't created a virtual environment, run

```bash
uv sync --dev
```

And finally add the dependency

```bash
uv add ../../packages/integration_testing --dev
```

To read more about how to write integration tests, check
out [integration tests](/docs/development/integrations/tests.md)
