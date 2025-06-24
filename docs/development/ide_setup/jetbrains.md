# JetBrains IDEs Setup Guide

This guide will help you configure JetBrains IDEs (like PyCharm, IntelliJ IDEA with Python plugin) for development in
the Google SecOps Marketplace Content Repository. Proper IDE configuration will enhance your development experience with
features like code completion, linting, and type checking.

## Initial Setup

### Project Setup

You have two options, to open the mono repo as a project or to open individual integrations as projects.
When opening a single integration as a project, you can set the python interpreter of the project to be the interpreter
found in the virtual environment of the integration.

1. **Open the project**:
    - Open PyCharm/IntelliJ
    - Select `File > Open` and navigate to your cloned repository
    - Select the repository root folder and click `Open`

2. **Configure Python Interpreter**:
    - Make sure to have `uv` installed in your system by running `pip install uv`
    - Go to `File > Settings > Project > Python Interpreter` (on macOS:
      `PyCharm > Preferences > Project > Python Interpreter`)
    - Click the gear icon and select `Add`
    - Choose `uv` and select wither `Generate New` or `Existing environment` if one exists or create a new one
    - Select a base interpreter with version 3.11 and your installed `uv` executable
    - Click `OK` to save your settings

## Recommended Plugins

To enhance your development experience, we recommend installing the following plugins:

### Essential Plugins

1. **Ruff**
    - **Purpose**: Provides integration with the Ruff linter and formatter
    - **Installation**: Go to `File > Settings > Plugins`, search for "Ruff" and install
    - **Configuration**:
        - Go to `File > Settings > Tools > Ruff`
        - Enable `Use Ruff formatter`
        - Set the path to Ruff executable (in your virtual environment)
        - Enable `Run on save`

2. **Mypy**
    - **Purpose**: Type checking integration
    - **Installation**: Go to `File > Settings > Plugins`, search for "Mypy" and install
    - **Configuration**:
        - Go to `File > Settings > Tools > Mypy`
        - Set the path to the Mypy executable (in your virtual environment)
        - Enable `Check effects` to show type errors in real-time

3. **Pydantic**
    - **Purpose**: Enhanced support for Pydantic models
    - **Installation**: Go to `File > Settings > Plugins`, search for "Pydantic" and install

4. **PyVenv Manage 2**
    - **Purpose**: Change the IDE's python interpreter
    - **Installation**: Go to `File > Settings > Plugins`, search for "PyVenv Manage 2" and install

### Additional Useful Plugins

1. **Rainbow Brackets**
    - **Purpose**: Colorizes matching brackets to improve code readability
    - **Installation**: Search for "Rainbow Brackets" in the plugin marketplace

2. **Key Promoter X**
    - **Purpose**: Learn keyboard shortcuts by showing notifications when you use the mouse for actions that have
      shortcuts
    - **Installation**: Search for "Key Promoter X" in the plugin marketplace

## Code Style Configuration

### Configuring Code Style

Enable the `ruff` plugin to handle import optimization and code reformatting on either save or code reformat.

As for IDE configurations, if you want, you can configure the following:

1. Go to `File > Settings > Editor > Code Style > Python`
2. Set the following options:
    - **Tabs and Indents**:
        - Use four spaces for indentation
        - Tab size: 4
        - Indent size: 4
    - **Spaces**:
        - Check appropriate boxes to match our [Code Style Guide](../code_style.md)
    - **Imports**:
        - Enable `Sort imports` and `Join imports with the same source`
        - Set import order to match our style guide (standard library, third-party, local)

### Configuring Line Length

1. Go to `File > Settings > Editor > Code Style`
2. Set the `Right margin (columns)` to 88 (to match Black/Ruff default)

### Python Integrated Tools

For consistent file headers:

1. Go to `File > Settings > Tools > Python Integrated Tools`
2. Under `Testing` set the `Default test runnin` to `Pytest`
3. Under `Docstring` set the `Docstring format` to `Google`

## Run Configurations

Here's an example of how to add one of `mp`'s commands as a run configuration to a project

### Setting Up Run Configurations for Running All Integration Tests

You can set up mp commands as run configurations

1. Go to `Run > Edit Configurations`
2. Click the `+` button and select `uv run`
3. Configure the following:
    - **Name**: Give it a descriptive name like "All Tests"
    - **Run**: Select `Module`
    - **Modules**: set to `mp`
    - **Arguments**: Add you arguments for mp. For this example `test --repository third_party`
    - **Python interpreter**: Select the `uv` interpreter that was configured earlier
    - Click `OK` to save

### MP CLI Tool Integration

To run the MP CLI tool directly from PyCharm:

1. Go to `Run > Edit Configurations`
2. Click the `+` button and select `Python`
3. Configure:
    - **Name**: "MP Format" (or another descriptive name)
    - **Script path**: Path to the MP CLI script
    - **Parameters**: `format` (or other commands as needed)
    - **Working directory**: Project root
    - **Python interpreter**: Your configured interpreter
    - Click `OK` to save

## Version Control Integration

1. Go to `File > Settings > Version Control > Git`
2. Ensure Git is properly configured with the path to your Git executable
3. Configure commit message templates if your team uses specific formats

## Project-Specific Settings

JetBrains IDEs can store project-specific settings in the `.idea` directory. For team-wide settings:

1. Configure `.idea/codeStyles` to share code style settings
2. Use `.idea/fileTemplates` for shared file templates
3. Consider adding appropriate entries to `.gitignore` for personal settings while keeping shared settings in version
   control

## Troubleshooting

### Common Issues

1. **Interpreter Not Found**:
    - Ensure your virtual environment is activated and properly configured
    - Check that all dependencies are installed in the environment

2. **Plugin Conflicts**:
    - If you experience conflicts between Ruff and other linting/formatting plugins, disable the conflicting plugins

3. **Performance Issues**:
    - Exclude large directories from indexing (like `.venv`, `build`, etc.) in
      `File > Settings > Project > Project Structure`

## Additional Resources

- [PyCharm Official Documentation](https://www.jetbrains.com/help/pycharm/)
- [JetBrains Python Plugin Documentation](https://www.jetbrains.com/help/idea/python.html) (for IntelliJ IDEA users)
- [Our Linters & Formatters Guide](../linters_formatters.md)

If you encounter any issues with your JetBrains IDE setup, please reach out to the repository maintainers.