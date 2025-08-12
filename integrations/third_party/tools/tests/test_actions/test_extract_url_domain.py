from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable, List

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import ExtractUrlDomain as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def _patch_params(monkeypatch, params: Dict[str, str]) -> None:
    Orig = Action.SiemplifyAction
    orig_init = Orig.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        try:
            p = dict(getattr(self, "parameters", {}) or {})
        except Exception:
            p = {}
        p.update(params)
        self.parameters = p

    def _extract(self, *a, **kw):
        key = kw.get("param_name") or (a[0] if a else None)
        default = kw.get("default_value", "")
        return str(params.get(str(key), default))

    def _noop_update_entities(self, updated_entities):
        return None

    monkeypatch.setattr(Orig, "__init__", _init, raising=True)
    monkeypatch.setattr(Orig, "extract_action_param", _extract, raising=True)
    monkeypatch.setattr(Orig, "update_entities", _noop_update_entities, raising=True)


def _set_entities(monkeypatch, ents: Iterable[tuple[str, str]]) -> list:
    lst = [SimpleNamespace(identifier=i, entity_type=t, additional_properties={}) for i, t in ents]
    monkeypatch.setattr(Action.SiemplifyAction, "target_entities", lst, raising=False)
    return lst


def _jo_list(obj: Any) -> List[Dict[str, Any]] | None:
    if obj is None:
        return None
    if isinstance(obj, list):
        return obj
    maybe = getattr(obj, "json_result", None)
    return maybe if isinstance(maybe, list) else None


def _find_in_json_list(items: List[Dict[str, Any]], entity_key: str) -> Dict[str, Any]:
    for it in items:
        if it.get("Entity") == entity_key:
            return it.get("EntityResult", {})
    return {}


class TestExtractURLDomain:
    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Separator": ",",
            "URLs": "",
            "Extract subdomain": "False",
        }
    )
    def test_entities_example_from_params_block(self, action_output: MockActionOutput, monkeypatch) -> None:
        entities = [
            ("YOUR NEW SALARY NOTIFICATION", "USERUNIQNAME"),
            ("<INSERT STRING>", "USERUNIQNAME"),
            ("VICKIE.B@SIEMPLIFY.CO", "USERUNIQNAME"),
            ("HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP", "DestinationURL"),
            ("F.ATTACKER4@GMAIL.COM", "USERUNIQNAME"),
        ]
        _patch_params(monkeypatch, {"Separator": ",", "URLs": "", "Extract subdomain": "False"})
        _set_entities(monkeypatch, entities)

        def _fake_gdfs(s: str, sub: bool) -> str | None:
            m = {
                "YOUR NEW SALARY NOTIFICATION": None,
                "<INSERT STRING>": None,
                "VICKIE.B@SIEMPLIFY.CO": "siemplify.co",
                "HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP": "markossolomon.com",
                "F.ATTACKER4@GMAIL.COM": "gmail.com",
            }
            return m.get(s)

        monkeypatch.setattr(Action, "get_domain_from_string", _fake_gdfs, raising=True)

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value) == "3"
        msg = action_output.results.output_message or ""
        assert "Domain extracted for ['VICKIE.B@SIEMPLIFY.CO', 'HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP', 'F.ATTACKER4@GMAIL.COM']" in msg
        assert "Failed extracting domain for ['YOUR NEW SALARY NOTIFICATION', '<INSERT STRING>']" in msg

        jl = _jo_list(action_output.results.json_output)
        assert isinstance(jl, list)
        assert _find_in_json_list(jl, "YOUR NEW SALARY NOTIFICATION").get("Error") == "Invalid domain or suffix"
        assert _find_in_json_list(jl, "<INSERT STRING>").get("Error") == "Invalid domain or suffix"
        assert _find_in_json_list(jl, "VICKIE.B@SIEMPLIFY.CO").get("domain") == "siemplify.co"
        assert _find_in_json_list(jl, "VICKIE.B@SIEMPLIFY.CO").get("source_entity_type") == "USERUNIQNAME"
        assert _find_in_json_list(jl, "HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP").get("domain") == "markossolomon.com"
        assert _find_in_json_list(jl, "HTTP://MARKOSSOLOMON.COM/F1Q7QX.PHP").get("source_entity_type") == "DestinationURL"
        assert _find_in_json_list(jl, "F.ATTACKER4@GMAIL.COM").get("domain") == "gmail.com"
        assert _find_in_json_list(jl, "F.ATTACKER4@GMAIL.COM").get("source_entity_type") == "USERUNIQNAME"

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Separator": ",",
            "URLs": "https://a.example.com/page, http://b.org?q=1, invalid",
            "Extract subdomain": "False",
        }
    )
    def test_urls_param_mixed_success_and_error(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(
            monkeypatch,
            {"Separator": ",", "URLs": "https://a.example.com/page, http://b.org?q=1, invalid", "Extract subdomain": "False"},
        )
        _set_entities(monkeypatch, [])

        def _fake_gdfs(s: str, sub: bool) -> str | None:
            if s.startswith("https://a.example.com"):
                return "example.com"
            if s.startswith("http://b.org"):
                return "b.org"
            return None

        monkeypatch.setattr(Action, "get_domain_from_string", _fake_gdfs, raising=True)

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value) == "2"
        jl = _jo_list(action_output.results.json_output)
        assert isinstance(jl, list)

        res_a = _find_in_json_list(jl, "https://a.example.com/page")
        assert res_a.get("domain") == "example.com"
        assert res_a.get("source_entity_type") in ("URL", "DestinationURL")

        res_b = _find_in_json_list(jl, "http://b.org?q=1")
        assert res_b.get("domain") == "b.org"
        assert res_b.get("source_entity_type") in ("URL", "DestinationURL")

        err = _find_in_json_list(jl, "invalid").get("Error", "")
        assert "Invalid" in err or "invalid" in err.lower()

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Separator": ",",
            "URLs": "http://sub.example.co.uk/x",
            "Extract subdomain": "True",
        }
    )
    def test_extract_subdomain_true_affects_result(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"Separator": ",", "URLs": "http://sub.example.co.uk/x", "Extract subdomain": "True"})
        _set_entities(monkeypatch, [])

        def _fake_gdfs(s: str, sub: bool) -> str | None:
            return "sub.example.co.uk" if sub else "example.co.uk"

        monkeypatch.setattr(Action, "get_domain_from_string", _fake_gdfs, raising=True)

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value) == "1"
        jl = _jo_list(action_output.results.json_output)
        assert isinstance(jl, list)
        assert _find_in_json_list(jl, "http://sub.example.co.uk/x").get("domain") == "sub.example.co.uk"

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Separator": ",",
            "URLs": "",
            "Extract subdomain": "False",
        }
    )
    def test_no_inputs_yields_zero_and_no_urls_processed_message(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"Separator": ",", "URLs": "", "Extract subdomain": "False"})
        _set_entities(monkeypatch, [])

        def _fake_gdfs(s: str, sub: bool) -> str | None:
            return None

        monkeypatch.setattr(Action, "get_domain_from_string", _fake_gdfs, raising=True)

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value) == "0"
        assert "No URLs processed" in (action_output.results.output_message or "")

    @set_metadata(
        parameters={
            "Scope": "All entities",
            "Test case": "8# Phishing email detector",
            "Integration Instance": "Default Environment_System Default Instance",
            "Separator": ",",
            "URLs": "http://ok.com, http://boom.com",
            "Extract subdomain": "False",
        }
    )
    def test_exception_in_get_domain_is_caught_and_reported(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"Separator": ",", "URLs": "http://ok.com, http://boom.com", "Extract subdomain": "False"})
        _set_entities(monkeypatch, [])

        def _fake_gdfs(s: str, sub: bool) -> str | None:
            if "boom.com" in s:
                raise RuntimeError("parse error")
            return "ok.com"

        monkeypatch.setattr(Action, "get_domain_from_string", _fake_gdfs, raising=True)

        Action.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert str(action_output.results.result_value) == "1"
        jl = _jo_list(action_output.results.json_output)
        assert isinstance(jl, list)
        assert _find_in_json_list(jl, "http://ok.com").get("domain") == "ok.com"
        assert "Exception:" in _find_in_json_list(jl, "http://boom.com").get("Error", "")
