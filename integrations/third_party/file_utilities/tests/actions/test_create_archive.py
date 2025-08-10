from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Tuple

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import CreateArchive as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def _mkfiles(dirpath: Path, names: list[str]) -> list[str]:
    dirpath.mkdir(parents=True, exist_ok=True)
    out: list[str] = []
    for n in names:
        p = dirpath / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
        out.append(str(p))
    return out


def _ok_make_archive(ret_path: str, calls: list[Tuple[tuple, dict[str, Any]]]):
    def _f(*a, **k):
        calls.append((a, k))
        return ret_path
    return _f


def _fake_extract_factory(params: dict[str, str]):
    def _extract(self, name, *a, **k):  # noqa: ANN001, ANN202
        return params.get(name, "")
    return _extract


def _extract_json(obj: Any) -> dict[str, Any] | None:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    jr = getattr(obj, "json_result", None)
    if isinstance(jr, dict):
        return jr
    return None


def _assert_success_output(action_output: MockActionOutput, archive_path: str) -> None:
    assert action_output.results.execution_state is ExecutionState.COMPLETED
    rv = "" if action_output.results.result_value is None else str(action_output.results.result_value)
    msg = "" if action_output.results.output_message is None else str(action_output.results.output_message)
    assert archive_path in (rv + msg)
    jo = _extract_json(action_output.results.json_output)
    assert isinstance(jo, dict) and jo.get("success") is True and archive_path in str(jo.get("archive", ""))


class TestCreateArchive:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive Type": "zip",
            "Archive Base Name": "logs_backup",
            "Archive Input": "<archive input>",
        }
    )
    def test_dir_input_happy_path(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src_dir = base / "inbox"
            _mkfiles(src_dir, ["a.log", "nested/b.log"])
            out_dir = base / "out"
            calls: list[Tuple[tuple, dict[str, Any]]] = []
            monkeypatch.setattr(Action, "DEST_DIR", str(out_dir), raising=True)
            monkeypatch.setattr(shutil, "make_archive", _ok_make_archive(str(out_dir / "logs_backup.zip"), calls), raising=True)
            params = {"Archive Type": "zip", "Archive Base Name": "logs_backup", "Archive Input": str(src_dir)}
            monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _fake_extract_factory(params), raising=True)
            Action.main()
        _assert_success_output(action_output, str(out_dir / "logs_backup.zip"))
        assert calls

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive Type": "zip",
            "Archive Base Name": "multi",
            "Archive Input": "<archive input>",
        }
    )
    def test_files_input_happy_path(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            files = _mkfiles(base / "src", ["a.txt", "b.txt"])
            out_dir = base / "out"
            calls: list[Tuple[tuple, dict[str, Any]]] = []
            monkeypatch.setattr(Action, "DEST_DIR", str(out_dir), raising=True)
            monkeypatch.setattr(shutil, "make_archive", _ok_make_archive(str(out_dir / "multi.zip"), calls), raising=True)
            params = {"Archive Type": "zip", "Archive Base Name": "multi", "Archive Input": ",".join(files)}
            monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _fake_extract_factory(params), raising=True)
            Action.main()
        _assert_success_output(action_output, str(out_dir / "multi.zip"))
        assert calls

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive Type": "zip",
            "Archive Base Name": "ensure_dir",
            "Archive Input": "<archive input>",
        }
    )
    def test_creates_destination_directory(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src_dir = base / "in"
            _mkfiles(src_dir, ["x.log"])
            out_dir = base / "new" / "deep" / "dir"
            calls: list[Tuple[tuple, dict[str, Any]]] = []
            monkeypatch.setattr(Action, "DEST_DIR", str(out_dir), raising=True)
            monkeypatch.setattr(shutil, "make_archive", _ok_make_archive(str(out_dir / "ensure_dir.zip"), calls), raising=True)
            params = {"Archive Type": "zip", "Archive Base Name": "ensure_dir", "Archive Input": str(src_dir)}
            monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _fake_extract_factory(params), raising=True)
            assert not os.path.exists(out_dir)
            Action.main()
        _assert_success_output(action_output, str(out_dir / "ensure_dir.zip"))
        assert calls

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive Type": "zip",
            "Archive Base Name": "mkdir_fail",
            "Archive Input": "<archive input>",
        }
    )
    def test_failed_status_when_dest_dir_mkdir_fails(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src_dir = base / "src"
            _mkfiles(src_dir, ["a.log"])
            out_dir = base / "bad" / "deep"

            def _mkdir_fail(*a, **k):
                raise OSError("mkdir denied")

            monkeypatch.setattr(Action, "DEST_DIR", str(out_dir), raising=True)
            monkeypatch.setattr(Path, "mkdir", _mkdir_fail, raising=True)
            monkeypatch.setattr(shutil, "make_archive", lambda *a, **k: str(out_dir / "mkdir_fail.zip"), raising=True)
            params = {"Archive Type": "zip", "Archive Base Name": "mkdir_fail", "Archive Input": str(src_dir)}
            monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _fake_extract_factory(params), raising=True)
            Action.main()

        assert action_output.results.execution_state is ExecutionState.FAILED
        rv = "" if action_output.results.result_value is None else str(action_output.results.result_value)
        msg = "" if action_output.results.output_message is None else str(action_output.results.output_message)
        assert any(x in (rv + msg) for x in ["mkdir", "fail", "Failed"])
