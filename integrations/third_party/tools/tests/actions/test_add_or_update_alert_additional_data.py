import json
from types import SimpleNamespace
from typing import Any, Dict

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from TIPCommon.base.action import ExecutionState
from ...actions import AddOrUpdateAlertAdditionalData as Action

def _patch_siemplify(monkeypatch, json_fields: str, alert_data: Dict[str, Any] | None, store: Dict[str, str]):
    monkeypatch.setattr(Action.SiemplifyAction, "parameters", {"Json Fields": json_fields}, raising=True)
    a = SimpleNamespace(identifier="A-1", additional_data=None if alert_data is None else json.dumps(alert_data))
    monkeypatch.setattr(Action.SiemplifyAction, "current_alert", property(lambda self: a), raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "update_alerts_additional_data", lambda self, d: store.update(d), raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "result", type("R", (), {"add_result_json": lambda self2, x: setattr(self2, "_jr", x)})(), raising=True)

class TestAddOrUpdateAlertAdditionalData:
    @set_metadata(parameters={"Json Fields": "{}"})
    def test_empty_json(self, action_output: MockActionOutput, monkeypatch) -> None:
        store: Dict[str, str] = {}
        _patch_siemplify(monkeypatch, "{}", None, store)
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = action_output.results.json_output
        assert isinstance(jo, dict)
        assert "dict" in jo and isinstance(jo["dict"], dict)
        assert "list" in jo and isinstance(jo["list"], list)
        assert action_output.results.result_value in (2, "2")

    @set_metadata(parameters={"Json Fields": '["x","y"]'})
    def test_appends_list(self, action_output: MockActionOutput, monkeypatch) -> None:
        store: Dict[str, str] = {}
        _patch_siemplify(monkeypatch, '["x","y"]', {"dict": {}, "list": ["z"]}, store)
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = action_output.results.json_output
        assert isinstance(jo, dict)
        assert all(i in jo["list"] for i in ["z", "x", "y"])

    @set_metadata(parameters={"Json Fields": '{"a":1,"b":2}'})
    def test_merges_dict(self, action_output: MockActionOutput, monkeypatch) -> None:
        store: Dict[str, str] = {}
        _patch_siemplify(monkeypatch, '{"a":1,"b":2}', {"dict": {"c": 3}, "list": []}, store)
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = action_output.results.json_output
        assert isinstance(jo, dict)
        assert jo["dict"]["a"] == 1 and jo["dict"]["b"] == 2 and jo["dict"]["c"] == 3

    @set_metadata(parameters={"Json Fields": '"raw"'})
    def test_raw_string_as_data(self, action_output: MockActionOutput, monkeypatch) -> None:
        store: Dict[str, str] = {}
        _patch_siemplify(monkeypatch, '"raw"', {"dict": {}, "list": []}, store)
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        jo = action_output.results.json_output
        assert isinstance(jo, dict)
        assert jo.get("data") == "raw"
