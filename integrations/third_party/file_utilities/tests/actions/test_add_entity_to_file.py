from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Tuple

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import AddEntityToFile as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class _FakeEFM:
    def __init__(self, path: str, timeout: int, initial: Iterable[str] | None = None, bag: list[Any] | None = None):
        self.path = path
        self.timeout = timeout
        self.entities = set(initial or [])
        self.added: list[str] = []
        if bag is not None:
            bag.append(self)

    def __enter__(self) -> "_FakeEFM":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    def addEntity(self, val: str) -> None:  # noqa: N802
        self.entities.add(val)
        self.added.append(val)


def _patch_extract(monkeypatch, params: Dict[str, str]) -> None:
    def _extract(self, *a, **kw):  # noqa: ANN001, ANN202
        key = kw.get("param_name") or (a[0] if a else None)
        default = kw.get("default_value", "")
        return params.get(str(key), default)
    monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _extract, raising=True)


def _patch_entities(monkeypatch, identifiers: Iterable[str]) -> None:
    ents = [SimpleNamespace(identifier=i) for i in identifiers]
    monkeypatch.setattr(Action.SiemplifyAction, "target_entities", ents, raising=False)


def _assert_lines(msg: str, must_have: List[str]) -> None:
    m = msg or ""
    for s in must_have:
        assert s in m


class TestAddEntityToFile:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_all_new_entities_added(self, action_output: MockActionOutput, monkeypatch) -> None:
        efm_bag: list[_FakeEFM] = []
        monkeypatch.setattr(Action, "EntityFileManager", lambda p, t: _FakeEFM(p, t, initial=[], bag=efm_bag), raising=True)
        _patch_entities(monkeypatch, ["one@example.com", "two.example.com"])
        _patch_extract(monkeypatch, {"Filename": "new.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.json_output is None
        assert action_output.results.result_value in (True, "True")
        _assert_lines(
            action_output.results.output_message or "",
            ["Added Entity: one@example.com", "Added Entity: two.example.com"],
        )
        assert efm_bag and efm_bag[-1].added == ["one@example.com", "two.example.com"]

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_all_entities_already_present(self, action_output: MockActionOutput, monkeypatch) -> None:
        initial = {
            "YOUR NEW SALARY NOTIFICATION",
            "<INSERT STRING>",
            "VICKIE.B@SIEMPLIFY.CO",
            "HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP",
            "F.ATTACKER4@GMAIL.COM",
        }
        efm_bag: list[_FakeEFM] = []
        monkeypatch.setattr(Action, "EntityFileManager", lambda p, t: _FakeEFM(p, t, initial=initial, bag=efm_bag), raising=True)
        _patch_entities(monkeypatch, list(initial))
        _patch_extract(monkeypatch, {"Filename": "exists.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (False, "False")
        _assert_lines(
            action_output.results.output_message or "",
            [
                "Entity is already in file: YOUR NEW SALARY NOTIFICATION",
                "Entity is already in file: <INSERT STRING>",
                "Entity is already in file: VICKIE.B@SIEMPLIFY.CO",
                "Entity is already in file: HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP",
                "Entity is already in file: F.ATTACKER4@GMAIL.COM",
            ],
        )
        assert efm_bag and efm_bag[-1].added == []

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_mixed_existing_and_new_entities(self, action_output: MockActionOutput, monkeypatch) -> None:
        efm_bag: list[_FakeEFM] = []
        monkeypatch.setattr(
            Action,
            "EntityFileManager",
            lambda p, t: _FakeEFM(p, t, initial={"dup@example.com"}, bag=efm_bag),
            raising=True,
        )
        _patch_entities(monkeypatch, ["dup@example.com", "fresh.example.com"])
        _patch_extract(monkeypatch, {"Filename": "mixed.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (False, "False")
        _assert_lines(
            action_output.results.output_message or "",
            ["Entity is already in file: dup@example.com", "Added Entity: fresh.example.com"],
        )
        assert efm_bag and efm_bag[-1].added == ["fresh.example.com"]

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_uses_filename_and_timeout(self, action_output: MockActionOutput, monkeypatch, tmp_path) -> None:
        efm_bag: list[_FakeEFM] = []
        monkeypatch.setattr(Action, "FILE_PATH", f"{tmp_path.as_posix()}/", raising=True)
        monkeypatch.setattr(Action, "EntityFileManager", lambda p, t: _FakeEFM(p, t, initial=set(), bag=efm_bag), raising=True)
        _patch_entities(monkeypatch, ["only.one"])
        _patch_extract(monkeypatch, {"Filename": "target.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert efm_bag, "EntityFileManager was not instantiated"
        inst = efm_bag[-1]
        assert inst.path.replace("\\", "/").endswith("/target.out")
        assert inst.path.startswith(tmp_path.as_posix())
        assert inst.timeout == Action.timeout
