# Welcome to the Google SecOps Marketplace Content Repository!

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![Maintenance](https://img.shields.io/maintenance/yes/2025)

> [!WARNING]
> Disclaimer: this repository is in Preview, and the structure might change in the future.
>
> **_Note:_** Currently only the community integrations are available in this repository

👋 Hello and welcome! This repository is the central hub for a wide array of content
related to the Google SecOps marketplace. Whether you're looking to connect Google
SecOps with other security tools, explore practical use-cases, or leverage powerful
development packages, you've come to the right place.

Our goal is to provide you with all the resources you need to effectively use, develop,
and contribute to the Google SecOps ecosystem.

## 🗺️ Navigating This Repository: Your Documentation Guide

To help you find your way around and make the most of what's available, we've structured
our documentation into several key areas.
Think of this section as your compass,
pointing you to detailed information, guides, and resources. Most of our in-depth
documentation resides in the [`docs/`](./docs) directory, with specific tools and
packages also having their own detailed README files.

---

### 🚀 Getting Started

New to the repository or Google SecOps integrations? Start here!

* **Understanding This Repository**: You're reading it!
  This file provides a high-level overview.
* **[Contributing to the Project](./docs/contributing.md)**: Mandatory steps for acquiring licenses for contribution to
  the project. Please make sure to read and follow the process in order for your pull requests to be able to be merged.
* **[Core Concepts](./docs/core_concepts.md)**: Learn about the
  fundamental principles behind Google SecOps integrations.
* **[Installation & Setup](./docs/development/installation_guide.md)**: General setup instructions
  for working with this repository's content.

---

### 🔗 Integrations

Discover how to connect Google SecOps with a multitude of other security products and
services.

* **Browse Available Integrations**: Explore the [`integrations/`](./integrations) directory to see the
  integrations we offer. Each integration typically has its own `pyproject.toml` and `definition.yaml` providing
  specific details.
* **[Marketplace Integration Development Guide](./docs/development/README.md)**:
  Understand how to work with marketplace integrations.
* **How-To Guides & Examples**:
    * **[Running & Testing Integrations](./docs/development/integrations/tests.md)**:
      Practical guides on configuring and
      using the integrations.
    * **[Code Examples](./docs/development/integrations/examples.md)**: Snippets and
      scenarios showcasing integration capabilities.

*[Building Your Own Integration](./docs/development/integrations/creating_integrations.md)
**:
Comprehensive
instructions and guidelines on how to develop, build, and package your custom
integrations.

---

### 💻 Development

Ready to dive deeper, fix a bug, or contribute your own enhancements?

* **Coding Standards & Style**:
    * **[Code Style Guide](docs/development/code_style.md)**: Our
      conventions for writing clean, consistent, and maintainable code.
    * **[Linters & Formatters](docs/development/linters_formatters.md)**: Information on
      the tools we use to
      enforce code quality (e.g., Ruff, Mypy).

---

### 🛠️ Supporting Tools & Packages

Explore the shared libraries and utilities designed to make your development process
smoother.

* **Shared Code Packages (`packages/`)**: Discover reusable libraries like `TIPCommon`
  and `EnvironmentCommon`. For detailed information, see the [`packages/README.md`](./packages/README.md).
* **Developer Utilities (`tools/`)**: Find scripts and command-line tools to assist with
  common development and operational tasks. For more details, see the [`tools/README.md`](./tools/README.md).
    * **Integration Zipper**: A utility to package integration versions. More details in
      its [dedicated README](./tools/zip_integration_by_version/README.md).
* **Marketplace CLI Tool (`mp`)**: [`packages/mp/README.md`](./packages/mp/README.md) -
  Your powerhouse for building, testing, and ensuring the quality of integrations. (Also
  linked from `packages/README.md`).

---

### 📜 Legal & Community

Important information regarding licensing and community conduct.

* **Licensing Information**: [LICENSE](./LICENSE) - Understand the terms under which the
  content in this repository is made available.
* **Code of Conduct**: [`docs/code_of_conduct.md`](./docs/code-of-conduct.md) - Our
  commitment to a welcoming, respectful, and inclusive community.
* **Security Policy**: (Future link: `SECURITY.md` or `docs/security.md`) - How to
  report security vulnerabilities.

---

We continuously strive to improve this repository and its documentation. If you have
suggestions or find something unclear, please don't hesitate to open an issue or
contribute!
