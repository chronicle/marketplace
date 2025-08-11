from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest

from ...actions import AddOrUpdateAlertAdditionalData as Action


class _Bag:
    def __init__(self) -> None:
        self.update_calls: List[Dict[str, str]] = []
        self.end_calls: List[tuple[str, Any]] = []
        self.json_output: Optional[dict] = None


class _FakeResult:
    def __init__(self, bag: _Bag) -> None:
        self._bag = bag

    def add_result_json(self, jo: dict) -> None:
        self._bag.json_output = jo


class _FakeAlert:
    def __init__(self, identifier: str, additional: Optional[dict | str]) -> None:
        self.identifier = identifier
        if isinstance(additional, dict):
            self.additional_data = json.dumps(additional)
        else:
            self.additional_data = additional


def _siemplify_factory(
    *,
    params: dict[str, str],
    initial_alert_json: Optional[dict | str] = None,
    bag: _Bag,
):
    class _FakeSiemplify:
        def __init__(self) -> None:
            self.parameters = params
            self.current_alert = _FakeAlert("A-1", initial_alert_json)
            self.result = _FakeResult(bag)
            self.LOGGER = SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None, exception=lambda *a, **k: None)

        def update_alerts_additional_data(self, mapping: dict[str, str]) -> None:
            bag.update_calls.append(mapping)
            if self.current_alert.identifier in mapping:
                self.current_alert.additional_data = mapping[self.current_alert.identifier]

        def end(self, message: str, result_value: Any) -> None:
            bag.end_calls.append((message, result_value))

    return _FakeSiemplify


def _jo(bag: _Bag) -> dict:
    assert isinstance(bag.json_output, dict)
    return bag.json_output  # type: ignore[return-value]


class TestAddOrUpdateAlertAdditionalData:
    def test_list_input_appends_to_empty_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bag = _Bag()
        params = {"Json Fields": '["a","b"]'}
        monkeypatch.setattr(Action, "SiemplifyAction", _siemplify_factory(params=params, initial_alert_json=None, bag=bag), raising=True)
        Action.main()
        assert len(bag.update_calls) == 1
        jo = _jo(bag)
        assert jo.get("dict") == {}
        assert jo.get("list") == ["a", "b"]
        assert bag.end_calls
        msg, rv = bag.end_calls[-1]
        assert "Alert data attached as JSON" in msg
        assert str(rv) == "2"

    def test_dict_input_merges_into_existing_alert_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bag = _Bag()
        existing = {"dict": {"x": 1}, "list": ["q"]}
        params = {"Json Fields": '{"y":2}'}
        monkeypatch.setattr(Action, "SiemplifyAction", _siemplify_factory(params=params, initial_alert_json=existing, bag=bag), raising=True)
        Action.main()
        assert len(bag.update_calls) == 1
        jo = _jo(bag)
        assert jo.get("dict") == {"x": 1, "y": 2}
        assert jo.get("list") == ["q"]
        msg, rv = bag.end_calls[-1]
        assert "Alert data attached as JSON" in msg
        assert str(rv) == "3" or str(rv) == "2"

    def test_string_input_is_stored_under_data_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bag = _Bag()
        params = {"Json Fields": "raw-value"}
        existing = {"dict": {}, "list": []}
        monkeypatch.setattr(Action, "SiemplifyAction", _siemplify_factory(params=params, initial_alert_json=existing, bag=bag), raising=True)
        Action.main()
        assert len(bag.update_calls) == 1
        jo = _jo(bag)
        assert jo.get("dict") == {}
        assert jo.get("list") == []
        assert jo.get("data") == "raw-value"
        msg, rv = bag.end_calls[-1]
        assert "Alert data attached as JSON" in msg
        assert str(rv) in {"2", "3"}

    def test_empty_json_keeps_defaults_and_does_not_call_update(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bag = _Bag()
        params = {"Json Fields": "{}"}
        monkeypatch.setattr(Action, "SiemplifyAction", _siemplify_factory(params=params, initial_alert_json=None, bag=bag), raising=True)
        Action.main()
        assert bag.update_calls == []
        jo = _jo(bag)
        assert jo.get("dict") == {}
        assert jo.get("list") == []
        msg, rv = bag.end_calls[-1]
        assert "Alert data attached as JSON" in msg
        assert str(rv) == "2"

    def test_malformed_json_is_treated_as_raw_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        bag = _Bag()
        params = {"Json Fields": '{"not: valid'}
        monkeypatch.setattr(Action, "SiemplifyAction", _siemplify_factory(params=params, initial_alert_json=None, bag=bag), raising=True)
        Action.main()
        assert len(bag.update_calls) == 1
        jo = _jo(bag)
        assert jo.get("dict") == {}
        assert jo.get("list") == []
        assert jo.get("data") == '{"not: valid'
        msg, rv = bag.end_calls[-1]
        assert "Alert data attached as JSON" in msg
        assert str(rv) in {"2", "3"}
