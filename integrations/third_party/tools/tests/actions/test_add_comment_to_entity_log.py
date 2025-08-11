from types import SimpleNamespace
from typing import Any, Dict, List, Tuple
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from TIPCommon.base.action import ExecutionState
from ...actions import AddCommentToEntityLog as Action
import pytest

def _fake_extract_factory(params: Dict[str, str]):
    def _extract(self, name: str, is_mandatory: bool = False, print_value: bool = False, input_type: str | None = None):
        return params.get(name, "")
    return _extract

class _Calls:
    def __init__(self) -> None:
        self.posts: List[Tuple[str, Dict[str, Any]]] = []

def _set_entities(monkeypatch: pytest.MonkeyPatch, entities: List[str]) -> None:
    monkeypatch.setattr(
        Action.SiemplifyAction,
        "target_entities",
        property(lambda self: [SimpleNamespace(identifier=e) for e in entities]),
        raising=True,
    )

def _patch_siemplify(
    monkeypatch: pytest.MonkeyPatch,
    params: Dict[str, str],
    entities: List[str],
    calls: _Calls,
    api_root: str = "http://localhost",
    environment: str = "Default",
    validate_ok: List[bool] | None = None,
) -> None:
    monkeypatch.setattr(Action.SiemplifyAction, "extract_action_param", _fake_extract_factory(params), raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "API_ROOT", api_root, raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "_environment", environment, raising=True)
    class _Resp:
        def __init__(self, ok: bool) -> None:
            self.status_code = 200 if ok else 500
            self.text = ""
    class _Session:
        def post(self, url: str, json: Dict[str, Any]):
            calls.posts.append((url, json))
            idx = len(calls.posts) - 1
            ok = True if validate_ok is None else validate_ok[min(idx, len(validate_ok) - 1)]
            return _Resp(ok)
    monkeypatch.setattr(Action.SiemplifyAction, "session", _Session(), raising=True)
    def _validate(self, r: Any) -> None:
        if r.status_code >= 400:
            raise RuntimeError("HTTP error")
    monkeypatch.setattr(Action.SiemplifyAction, "validate_siemplify_error", _validate, raising=True)
    monkeypatch.setattr(Action.SiemplifyAction, "result", type("R", (), {"add_result_json": lambda self2, x: None})(), raising=True)
    _set_entities(monkeypatch, entities)

class TestAddCommentToEntityLog:
    @set_metadata(parameters={"User": "@Admin", "Comment": "text"})
    def test_happy_path(self, action_output: MockActionOutput, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _Calls()
        _patch_siemplify(monkeypatch, {"User": "@Admin", "Comment": "text"}, ["A", "B"], calls, "https://api", "Env")
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.posts) == 2
        for url, payload in calls.posts:
            assert url.endswith("/external/v1/entities/AddNote?format=camel")
            assert payload["author"] == "@Admin"
            assert payload["content"] == "text"
            assert payload["entityEnvironment"] == "Env"
            assert payload["id"] == 0

    @set_metadata(parameters={"User": "user", "Comment": ""})
    def test_empty_comment(self, action_output: MockActionOutput, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _Calls()
        _patch_siemplify(monkeypatch, {"User": "user", "Comment": ""}, ["One"], calls)
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.posts) == 1
        assert calls.posts[0][1]["content"] == ""

    @set_metadata(parameters={"User": "fail", "Comment": "boom"})
    def test_api_failure_exception(self, action_output: MockActionOutput, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _Calls()
        _patch_siemplify(monkeypatch, {"User": "fail", "Comment": "boom"}, ["X", "Y"], calls, validate_ok=[True, False])
        with pytest.raises(RuntimeError):
            Action.main()
        assert len(calls.posts) == 2

    @set_metadata(parameters={"User": "u", "Comment": "ok"})
    def test_custom_api_root_and_env(self, action_output: MockActionOutput, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _Calls()
        _patch_siemplify(monkeypatch, {"User": "u", "Comment": "ok"}, ["entity"], calls, "https://srv", "Prod")
        Action.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert len(calls.posts) == 1
        url, payload = calls.posts[0]
        assert url.startswith("https://srv")
        assert payload["entityEnvironment"] == "Prod"
