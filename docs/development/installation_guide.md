# Installation Guide

This document provides detailed instructions for setting up the Marketplace project on your local environment.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.11 or higher
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/marketplace.git](https://github.com/your-username/marketplace.git) cd marketplace
```

### 2. Set Up Your Environment

The project uses `uv` to handle integrations' projects and dependencies

```bash
pip install uv
```

And install the marketplace package

```bash
pip install ${repo_root}/packages/mp}
```

For more information about `mp` check the [documentation](/packages/mp/README.md)