import pytest
from typer.testing import CliRunner

from mp.check import app

runner = CliRunner()

def test_check_command_summarize_flag(mocker):
    # Mock the lint_python_files function to return a controlled output
    mock_lint_output = """
file1.py:10:5: E001 Missing docstring (pydocstyle)
file2.py:20:1: F401 'os' imported but unused (pyflakes)
file3.py:30:10: E001 Another missing docstring (pydocstyle)
file4.py:40:1: F401 'sys' imported but unused (pyflakes)
"""
    mocker.patch("mp.core.code_manipulation.lint_python_files", return_value=mock_lint_output)
    mocker.patch("mp.core.file_utils.is_python_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("mp.core.unix.get_changed_files", return_value=["file1.py", "file2.py", "file3.py", "file4.py"])

    result = runner.invoke(app, ["--changed-files", "--summarize"])

    assert result.exit_code == 0
    assert "--- Ruff Issue Summary ---" in result.stdout
    assert "- E001: 2 occurrences - Missing docstring" in result.stdout
    assert "- F401: 2 occurrences - 'os' imported but unused" in result.stdout
    assert "--------------------------" in result.stdout

def test_check_command_no_summarize_flag(mocker):
    mock_lint_output = """
file1.py:10:5: E001 Missing docstring (pydocstyle)
"""
    mocker.patch("mp.core.code_manipulation.lint_python_files", return_value=mock_lint_output)
    mocker.patch("mp.core.file_utils.is_python_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("mp.core.unix.get_changed_files", return_value=["file1.py"])

    result = runner.invoke(app, ["--changed-files"])

    assert result.exit_code == 0
    assert "--- Ruff Issue Summary ---" not in result.stdout
    assert "E001 Missing docstring" in result.stdout # Ensure raw output is still there
