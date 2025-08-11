from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import ExtractArchive as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def _mkzip(tmp: Path, name: str, files: list[str]) -> Path:
    src = tmp / f"{name}_src"
    src.mkdir(parents=True, exist_ok=True)
    for f in files:
        p = src / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    out = shutil.make_archive(str(tmp / name), "zip", str(src))
    return Path(out)


def _jo(obj: Any) -> dict[str, Any] | None:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    jr = getattr(obj, "json_result", None)
    return jr if isinstance(jr, dict) else None


def _tree_contains(node: dict, name: str) -> bool:
    if not isinstance(node, dict):
        return False
    if node.get("name") == name:
        return True
    for child in node.get("children", []) or []:
        if _tree_contains(child, name):
            return True
    return False


def _patch_params(monkeypatch, archive_value: str) -> None:
    Orig = Action.SiemplifyAction
    orig_init = Orig.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        try:
            params = dict(getattr(self, "parameters", {}) or {})
        except Exception:
            params = {}
        params["Archive"] = archive_value
        self.parameters = params

    monkeypatch.setattr(Orig, "__init__", _init, raising=True)


class TestExtractArchive:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive": "<archive file with path>",
        }
    )
    def test_single_archive_success(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            arc = _mkzip(base, "logs_backup", ["a.txt", "nested/b.txt"])
            dest_dir = base / "extract_root"
            monkeypatch.setattr(Action, "DEST_DIR", str(dest_dir), raising=True)
            _patch_params(monkeypatch, str(arc))

            Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (True, "True")
        msg = "" if action_output.results.output_message is None else str(action_output.results.output_message)
        assert "Successfully extracted archive" in msg and arc.name in msg

        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        archives = jo.get("archives")
        assert isinstance(archives, list) and len(archives) == 1
        item = archives[0]
        assert item.get("success") is True
        assert item.get("archive") == arc.name
        assert Path(item.get("folder", "")).resolve() == (dest_dir / arc.stem).resolve()
        assert isinstance(item.get("files"), dict)
        assert set(item.get("files_list", [])) & {"a.txt", "b.txt"}

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive": "<archive file with path>",
        }
    )
    def test_multiple_archives_success(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            arc1 = _mkzip(base, "rpt1", ["x.log"])
            arc2 = _mkzip(base, "rpt2", ["y.log", "z.txt"])
            dest_dir = base / "dest_multi"
            monkeypatch.setattr(Action, "DEST_DIR", str(dest_dir), raising=True)
            _patch_params(monkeypatch, f"{arc1},{arc2}")

            Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (True, "True")

        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        archives = jo.get("archives")
        assert isinstance(archives, list) and len(archives) == 2
        names = {arc1.name, arc2.name}
        got = {a.get("archive") for a in archives}
        assert names == got
        for a in archives:
            assert a.get("success") is True
            assert Path(a.get("folder", "")).resolve().parent == dest_dir.resolve()

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive": "<archive file with path>",
        }
    )
    def test_existing_output_dir_is_used(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            arc = _mkzip(base, "precreated", ["q.txt"])
            dest_dir = base / "extract_here"
            pre = dest_dir / arc.stem
            pre.mkdir(parents=True, exist_ok=True)
            monkeypatch.setattr(Action, "DEST_DIR", str(dest_dir), raising=True)
            _patch_params(monkeypatch, str(arc))

            Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict) and isinstance(jo.get("archives"), list)
        item = jo["archives"][0]
        assert item.get("success") is True
        assert Path(item.get("folder", "")).resolve() == pre.resolve()

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Archive": "<archive file with path>",
        }
    )
    def test_json_contains_files_with_path_and_tree(self, action_output: MockActionOutput, monkeypatch) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            arc = _mkzip(base, "tree", ["root.txt", "d1/d2/inner.txt"])
            dest_dir = base / "extract_json"
            monkeypatch.setattr(Action, "DEST_DIR", str(dest_dir), raising=True)
            _patch_params(monkeypatch, str(arc))

            Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        archives = jo.get("archives")
        assert isinstance(archives, list) and archives[0].get("success") is True

        item = archives[0]
        files_with_path = item.get("files_with_path", [])
        assert isinstance(files_with_path, list) and files_with_path
        assert any(Path(p).name == "root.txt" for p in files_with_path)

        tree = item.get("files")
        assert isinstance(tree, dict)
        assert _tree_contains(tree, "inner.txt")
