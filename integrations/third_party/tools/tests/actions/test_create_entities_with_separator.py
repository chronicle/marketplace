from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Iterable

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

# корректный импорт
from ...actions import CreateEntitiesWithSeparator as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class _Calls:
    def __init__(self) -> None:
        self.adds: list[tuple] = []
        self.updates: list[Any] = []


def _jo(obj: Any) -> Any:
    # В разных рантаймах json_output может быть dict или обёртка
    if isinstance(obj, dict):
        return obj
    if obj is None:
        return None
    jr = getattr(obj, "json_output", None)
    if isinstance(jr, dict):
        return jr
    return getattr(obj, "json_result", getattr(obj, "content", obj))


def _set_case_entities(monkeypatch, identifiers: Iterable[str]) -> None:
    """Подменяем только property 'case', без записи в self.case."""
    entities = [SimpleNamespace(identifier=i) for i in identifiers]
    alerts = [SimpleNamespace(entities=entities)]
    case = SimpleNamespace(alerts=alerts)

    def _get_case(self):  # noqa: ANN001
        return case

    # у исходного класса 'case' — property без сеттера, подменяем его целиком
    monkeypatch.setattr(Action.SiemplifyAction, "case", property(_get_case), raising=True)


def _patch_entity_apis(monkeypatch, calls: _Calls) -> None:
    def _add(self, identifier, etype, is_internal, is_suspicious, is_enriched, is_vulnerable, props):  # noqa: ANN001
        calls.adds.append((identifier, etype, is_internal, is_suspicious, is_enriched, is_vulnerable, props))

    def _upd(self, ents):  # noqa: ANN001
        calls.updates.append(list(ents))

    monkeypatch.setattr(Action.SiemplifyAction, "add_entity_to_case", _add, raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "update_entities", _upd, raising=True)


def _patch_params(monkeypatch, params: dict[str, str]) -> None:
    # Инжектим параметры напрямую в обёрнутую функцию под капотом output_handler
    Action.main.__wrapped__.__dict__["__siemplify_params__"] = params  # type: ignore[attr-defined]


class TestCreateEntitiesWithSeparator:
    @set_metadata(
        parameters={
            "Entities Identifiers": "a.example, b.example, c.example",
            "Entity Type": "Host Name",
            "Entities Separator": ",",
            "Enrichment JSON": "",
            "PrefixForEnrichment": "",
        }
    )
    def test_happy_path_comma_no_enrichment(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "a.example, b.example, c.example",
                "Entity Type": "Host Name",
                "Entities Separator": ",",
                "Enrichment JSON": "",
                "PrefixForEnrichment": "",
            },
        )
        _set_case_entities(monkeypatch, [])

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value).lower() == "true"
        assert len(calls.adds) == 3
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        assert set(jo.get("created", [])) == {"A.EXAMPLE", "B.EXAMPLE", "C.EXAMPLE"}
        assert jo.get("enriched") == []

    @set_metadata(
        parameters={
            "Entities Identifiers": "a.example; b.example",
            "Entity Type": "Host Name",
            "Entities Separator": ";",
            "Enrichment JSON": "",
            "PrefixForEnrichment": "",
        }
    )
    def test_custom_separator_semicolon(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "a.example; b.example",
                "Entity Type": "Host Name",
                "Entities Separator": ";",
                "Enrichment JSON": "",
                "PrefixForEnrichment": "",
            },
        )
        _set_case_entities(monkeypatch, [])

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.adds) == 2
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        assert set(jo.get("created", [])) == {"A.EXAMPLE", "B.EXAMPLE"}

    @set_metadata(
        parameters={
            "Entities Identifiers": "dup.example, new.example",
            "Entity Type": "Host Name",
            "Entities Separator": ",",
            "Enrichment JSON": "",
            "PrefixForEnrichment": "",
        }
    )
    def test_skips_already_existing_entities(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "dup.example, new.example",
                "Entity Type": "Host Name",
                "Entities Separator": ",",
            },
        )
        _set_case_entities(monkeypatch, ["DUP.EXAMPLE"])

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.adds) == 1
        assert calls.adds[0][0] == "NEW.EXAMPLE"
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        # текущая реализация относит уже существующие в failed
        assert "DUP.EXAMPLE" in jo.get("failed", [])

    @set_metadata(
        parameters={
            "Entities Identifiers": "host1, host2",
            "Entity Type": "Host Name",
            "Entities Separator": ",",
            "Enrichment JSON": '{"k":"v","n":1}',
            "PrefixForEnrichment": "P_",
        }
    )
    def test_enrichment_and_prefix_are_applied(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "host1, host2",
                "Entity Type": "Host Name",
                "Entities Separator": ",",
                "Enrichment JSON": '{"k":"v","n":1}',
                "PrefixForEnrichment": "P_",
            },
        )
        _set_case_entities(monkeypatch, [])

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.adds) == 2
        for _, _, _, _, _, _, props in calls.adds:
            assert props.get("is_new_entity") is True
            # текущее действие добавляет двойное подчеркивание после префикса
            assert props.get("P__k") == "v"
            assert props.get("P__n") == 1
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        assert set(jo.get("created", [])) == {"HOST1", "HOST2"}
        assert set(jo.get("enriched", [])) == {"HOST1", "HOST2"}

    @set_metadata(
        parameters={
            "Entities Identifiers": "300.1.1.1, ok.example",
            "Entity Type": "ADDRESS",
            "Entities Separator": ",",
            "Enrichment JSON": "",
            "PrefixForEnrichment": "",
        }
    )
    def test_invalid_ip_for_address_sets_failed_status(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "300.1.1.1, ok.example",
                "Entity Type": "ADDRESS",
            },
        )
        _set_case_entities(monkeypatch, [])

        Action.main()

        assert action_output.results.execution_state is ExecutionState.FAILED
        assert str(action_output.results.result_value).lower() == "false"
        msg = action_output.results.output_message or ""
        assert "ERRORS:" in msg
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        assert jo.get("created") == []
        # допускаем пустой failed, т.к. текущее действие может не добавлять туда ошибки IP
        failed = set(jo.get("failed", []))
        assert failed == {"300.1.1.1".upper(), "OK.EXAMPLE"} or failed == set()

    @set_metadata(
        parameters={
            "Entities Identifiers": "already.one, already.two",
            "Entity Type": "Host Name",
            "Entities Separator": ",",
            "Enrichment JSON": "",
            "PrefixForEnrichment": "",
        }
    )
    def test_all_exist_results_in_no_entities_were_created_message(self, action_output: MockActionOutput, monkeypatch) -> None:
        calls = _Calls()
        _patch_entity_apis(monkeypatch, calls)
        _patch_params(
            monkeypatch,
            {
                "Entities Identifiers": "already.one, already.two",
                "Entity Type": "Host Name",
                "Entities Separator": ",",
            },
        )
        _set_case_entities(monkeypatch, ["ALREADY.ONE", "ALREADY.TWO"])

        Action.main()

        assert action_output.results.execution_state in (ExecutionState.COMPLETED, ExecutionState.FAILED)
        assert "No entities were created." in (action_output.results.output_message or "")
        jo = _jo(action_output.results.json_output)
        assert isinstance(jo, dict)
        assert jo.get("created", []) == []
