# Google SecOps SOAR SDK

> [!WARNING]
> **Disclaimer:** The SOAR SDK is currently a **work in progress** and is intended for **reference
only**. The code provided in the SDK does not reflect the code that is being used in the Google
> SecOps SOAR product.

The Google SecOps SOAR SDK is a development toolkit designed to help you build and test
integrations. It provides a set of tools and libraries to streamline the development process for
SOAR components.

For official and detailed documentation, please refer to the
[Google Cloud SOAR Documentation](https://cloud.google.com/chronicle/docs/secops/google-secops-soar-toc)

## How to Add the SDK to Your Integration

Since the SDK's source is in our backend and not yet the GitHub repository, it should be added to
your integration as a **development dependency**.
This means this package will be available in your development environment for testing
locally and type hinting but won't be packaged with your integration when it's deployed.
Nonetheless, the SDK will be available at runtime because it is already packaged and natively
available for all scripts in Google SecOps.

To add the SOAR SDK to your integration run

```bash
# from your integration's root folder
uv addc --dev git+https://github.com/chronicle/soar-sdk.git
```

* Note: it's important to have it only in the dev dependencies for now. If it's in the production
  dependencies, it can prevent the integration from being run correctly

Your `pyproject.toml` should look something like this:

```toml
[dependency-groups]
dev = [
    # ... other dev dependencies ...
    "soar-sdk",
    # ...
]

[tool.uv.sources]
# ... other sources ...
soar-sdk = { git = "https://github.com/chronicle/soar-sdk.git" }
# ...
```

After updating the `pyproject.toml` file, run the following command from your integration's root
directory to install the dev dependencies:

```bash
uv sync --dev
```
