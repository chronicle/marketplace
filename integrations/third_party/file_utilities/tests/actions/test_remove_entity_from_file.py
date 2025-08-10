from __future__ import annotations

from types import SimpleNamespace
from typing import Iterable

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import RemoveEntityFromFile as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class FakeEntityFileManager:
    def __init__(self, path: str, timeout: int, initial_entities: Iterable[str] | None = None, bag=None):
        self.path = path
        self.timeout = timeout
        self.entities = set(initial_entities or [])
        self.removed = []
        self.not_found = []
        if bag is not None:
            bag.append(self)

    def __enter__(self) -> FakeEntityFileManager:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def removeEntity(self, entity_id: str) -> None:
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            self.removed.append(entity_id)
        else:
            self.not_found.append(entity_id)


def patch_entities(monkeypatch, identifiers: Iterable[str]) -> None:
    monkeypatch.setattr(Action.SiemplifyAction, "target_entities", [SimpleNamespace(identifier=i) for i in identifiers])


def patch_extract(monkeypatch, params: dict) -> None:
    def _extract(self, param_name: str, *_, **__):
        return params.get(param_name)
    monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _extract, raising=True)


class TestRemoveEntityFromFile:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_remove_all_entities_success(self, action_output: MockActionOutput, monkeypatch) -> None:
        efm_bag = []
        initial_entities = [
            "YOUR NEW SALARY NOTIFICATION",
            "<INSERT STRING>",
            "VICKIE.B@SIEMPLIFY.CO",
            "HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP",
            "F.ATTACKER4@GMAIL.COM",
        ]
        monkeypatch.setattr(
            Action,
            "EntityFileManager",
            lambda p, t: FakeEntityFileManager(p, t, initial_entities, efm_bag),
            raising=True,
        )
        patch_entities(monkeypatch, initial_entities)
        patch_extract(monkeypatch, {"Filename": "testfile.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (True, "True")
        msg = action_output.results.output_message or ""
        for ent in initial_entities:
            assert f"Removed Entity: {ent}" in msg
        # проверяем, что в менеджере ничего не осталось
        assert not efm_bag[-1].entities

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_entity_not_found(self, action_output: MockActionOutput, monkeypatch) -> None:
        efm_bag = []
        initial_entities = ["exist@example.com"]
        monkeypatch.setattr(
            Action,
            "EntityFileManager",
            lambda p, t: FakeEntityFileManager(p, t, initial_entities, efm_bag),
            raising=True,
        )
        patch_entities(monkeypatch, ["notfound@example.com"])
        patch_extract(monkeypatch, {"Filename": "file.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value in (False, "False")
        msg = action_output.results.output_message or ""
        assert "Entity not found in file: notfound@example.com" in msg
        # сущность осталась в файле
        assert "exist@example.com" in efm_bag[-1].entities

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Filename": "<filename.out>",
        }
    )
    def test_partial_removal(self, action_output: MockActionOutput, monkeypatch) -> None:
        efm_bag = []
        initial_entities = ["keep@example.com", "remove@example.com"]
        monkeypatch.setattr(
            Action,
            "EntityFileManager",
            lambda p, t: FakeEntityFileManager(p, t, initial_entities, efm_bag),
            raising=True,
        )
        patch_entities(monkeypatch, ["remove@example.com", "missing@example.com"])
        patch_extract(monkeypatch, {"Filename": "partial.out"})

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        msg = action_output.results.output_message or ""
        assert "Removed Entity: remove@example.com" in msg
        assert "Entity not found in file: missing@example.com" in msg
        # "keep@example.com" осталась в файле
        assert "keep@example.com" in efm_bag[-1].entities
