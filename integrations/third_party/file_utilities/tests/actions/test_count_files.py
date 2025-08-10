from __future__ import annotations

import glob
from typing import Any, List, Tuple

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import CountFiles

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def _make_glob_stub(return_list: List[str], capture: list[Tuple[str, dict[str, Any]]]):
    def _stub(pattern: str, **kwargs: Any) -> List[str]:
        capture.append((pattern, kwargs))
        return return_list
    return _stub


def _assert_msg_is_num_or_empty(msg: object, expected: int) -> None:
    if msg is None:
        return
    if isinstance(msg, int):
        assert msg == expected
        return
    s = str(msg).strip()
    assert s in (str(expected), "")


class TestCountFilesScopeUi:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "File Extension": "dtfvhj*.txt",
            "Folder": "/tempFolder",
            "Is Recursive": "True",
        }
    )
    def test_no_matches_returns_zero(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls: list[Tuple[str, dict[str, Any]]] = []
        monkeypatch.setattr(glob, "glob", _make_glob_stub([], calls), raising=True)
        CountFiles.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (0, "0")
        _assert_msg_is_num_or_empty(action_output.results.output_message, 0)
        assert action_output.results.json_output is None
        assert calls
        pattern, kwargs = calls[-1]
        assert pattern.endswith("/dtfvhj*.txt") and pattern.startswith("/tempFolder")
        assert kwargs.get("recursive") in (True, "True")

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "File Extension": "*.txt",
            "Folder": "/anyFolder",
            "Is Recursive": "True",
        }
    )
    def test_recursive_counts_nested_txt(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls: list[Tuple[str, dict[str, Any]]] = []
        monkeypatch.setattr(glob, "glob", _make_glob_stub(
            ["/anyFolder/a.txt", "/anyFolder/nested/c.txt", "/anyFolder/nested/deep/d.txt"], calls
        ), raising=True)
        CountFiles.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        rv = action_output.results.result_value
        rv_int = int(rv) if isinstance(rv, str) else rv
        assert rv_int == 3
        _assert_msg_is_num_or_empty(action_output.results.output_message, 3)
        assert action_output.results.json_output is None
        pattern, kwargs = calls[-1]
        assert pattern.endswith("/*.txt") and pattern.startswith("/anyFolder")
        assert kwargs.get("recursive") in (True, "True")

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "File Extension": "*.txt",
            "Folder": "/rootOnly",
            "Is Recursive": "False",
        }
    )
    def test_non_recursive_counts_only_top_level(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls: list[Tuple[str, dict[str, Any]]] = []
        monkeypatch.setattr(glob, "glob", _make_glob_stub(
            ["/rootOnly/a.txt", "/rootOnly/b.txt"], calls
        ), raising=True)
        CountFiles.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        rv = action_output.results.result_value
        rv_int = int(rv) if isinstance(rv, str) else rv
        assert rv_int == 2
        _assert_msg_is_num_or_empty(action_output.results.output_message, 2)
        assert action_output.results.json_output is None
        pattern, kwargs = calls[-1]
        assert pattern.endswith("/*.txt") and pattern.startswith("/rootOnly")
        assert kwargs.get("recursive") in (False, "False", None)

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "File Extension": "",
            "Folder": "/mixed",
            "Is Recursive": "False",
        }
    )
    def test_missing_extension_defaults_to_all_files(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls: list[Tuple[str, dict[str, Any]]] = []
        monkeypatch.setattr(glob, "glob", _make_glob_stub(
            ["/mixed/a.txt", "/mixed/b.log"], calls
        ), raising=True)
        CountFiles.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        rv = action_output.results.result_value
        rv_int = int(rv) if isinstance(rv, str) else rv
        assert rv_int == 2
        _assert_msg_is_num_or_empty(action_output.results.output_message, 2)
        assert action_output.results.json_output is None
        pattern, kwargs = calls[-1]
        assert pattern.endswith("/*.*") and pattern.startswith("/mixed")
        assert kwargs.get("recursive") in (False, "False", None)
