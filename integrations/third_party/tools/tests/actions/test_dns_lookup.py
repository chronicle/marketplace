from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Tuple

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import DnsLookup as Action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def _patch_params(monkeypatch, params: Dict[str, str]) -> None:
    Orig = Action.SiemplifyAction
    orig_init = Orig.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        cur = dict(getattr(self, "parameters", {}) or {})
        cur.update(params)
        self.parameters = cur

    monkeypatch.setattr(Orig, "__init__", _init, raising=True)


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


def _find_for_entity(items: List[Dict[str, Any]], entity_key: str) -> List[Dict[str, Any]]:
    for it in items:
        if it.get("Entity") == entity_key:
            er = it.get("EntityResult")
            if isinstance(er, list):
                return er
    return []


class _FakePTRAnswer:
    def __init__(self, value: str) -> None:
        self.rrset = [value]


class _FakeRRSet:
    def __init__(self, rdtype: Any, values: List[str]) -> None:
        self.rdtype = rdtype
        self._values = values

    def __getitem__(self, idx: int) -> Any:
        class _V:
            def __init__(self, s: str) -> None:
                self._s = s

            def __str__(self) -> str:
                return self._s

        return _V(self._values[idx])


class _FakeDnsMsg:
    def __init__(self, answers: List[_FakeRRSet]) -> None:
        self.answer = answers


def _patch_dnspython_for_ptr(monkeypatch, mapping: Dict[Tuple[str, str], _FakePTRAnswer]) -> None:
    class _Res:
        def __init__(self, configure: bool = False) -> None:
            self.nameservers: List[str] = []

        def resolve_address(self, ip: str) -> _FakePTRAnswer | None:
            key = (self.nameservers[0] if self.nameservers else "", ip)
            return mapping.get(key)

    monkeypatch.setattr(Action.dns.resolver, "Resolver", _Res, raising=True)


def _patch_dnspython_for_hostname(monkeypatch, resp_by_server: Dict[Tuple[str, str], _FakeDnsMsg]) -> None:
    def _make_query(name: str, rdt: Any) -> Tuple[str, Any]:
        return (name, rdt)

    def _udp(query: Tuple[str, Any], server: str) -> _FakeDnsMsg:
        name, _rdt = query
        return resp_by_server.get((server.strip(), name), _FakeDnsMsg([]))

    def _to_text(rt: Any) -> str:
        if isinstance(rt, str):
            return rt
        mp = {1: "A", 15: "MX", 16: "TXT", 2: "NS", 5: "CNAME", 6: "SOA"}
        return mp.get(rt, str(rt))

    monkeypatch.setattr(Action.dns.message, "make_query", _make_query, raising=True)
    monkeypatch.setattr(Action.dns.query, "udp", _udp, raising=True)
    monkeypatch.setattr(Action.dns.rdatatype, "to_text", _to_text, raising=True)


class TestDnsLookup:
    @set_metadata(
        parameters={
            "DNS Servers": "1.1.1.1",
            "Data Type": "ANY",
        }
    )
    def test_ptr_lookup_success_for_address_entity(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"DNS Servers": "1.1.1.1", "Data Type": "ANY"})
        _set_entities(monkeypatch, [("93.184.216.34", "ADDRESS")])
        _patch_dnspython_for_ptr(monkeypatch, {("1.1.1.1", "93.184.216.34"): _FakePTRAnswer("edge.example.")})

        Action.main()

        assert action_output.results.execution_state in (ExecutionState.COMPLETED, None)
        assert str(action_output.results.result_value).lower() in ("true", "false", "True".lower())
        jo = _jo_list(action_output.results.json_output)
        assert isinstance(jo, list)
        rows = _find_for_entity(jo, "93.184.216.34")
        assert any(r.get("Type") == "PTR" and "edge.example." in str(r.get("Response")) and r.get("DNS Server") == "1.1.1.1" for r in rows)
        assert (action_output.results.output_message or "").strip() in ("Results Found",)

    @set_metadata(
        parameters={
            "DNS Servers": "1.1.1.1",
            "Data Type": "ANY",
        }
    )
    def test_hostname_any_returns_multiple_records(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"DNS Servers": "1.1.1.1", "Data Type": "ANY"})
        _set_entities(monkeypatch, [("example.com", "HOSTNAME")])
        resp = {
            ("1.1.1.1", "example.com"): _FakeDnsMsg(
                [
                    _FakeRRSet(1, ["93.184.216.34"]),
                    _FakeRRSet(15, ["10 mail.example.com."]),
                    _FakeRRSet(16, ['"v=spf1 -all"']),
                ]
            )
        }
        _patch_dnspython_for_hostname(monkeypatch, resp)

        Action.main()

        assert action_output.results.execution_state in (ExecutionState.COMPLETED, None)
        jo = _jo_list(action_output.results.json_output)
        assert isinstance(jo, list)
        rows = _find_for_entity(jo, "example.com")
        types = {r.get("Type") for r in rows}
        assert {"A", "MX", "TXT"}.issubset(types)
        assert any(r.get("DNS Server") == "1.1.1.1" for r in rows)
        assert "Results Found" in (action_output.results.output_message or "")

    @set_metadata(
        parameters={
            "DNS Servers": "9.9.9.9, 1.1.1.1",
            "Data Type": "ANY",
        }
    )
    def test_multiple_servers_first_empty_second_returns_answer(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"DNS Servers": "9.9.9.9, 1.1.1.1", "Data Type": "ANY"})
        _set_entities(monkeypatch, [("multi.example", "HOSTNAME")])
        resp = {
            ("1.1.1.1", "multi.example"): _FakeDnsMsg([_FakeRRSet(1, ["203.0.113.10"])])
        }
        _patch_dnspython_for_hostname(monkeypatch, resp)

        Action.main()

        jo = _jo_list(action_output.results.json_output)
        assert isinstance(jo, list)
        rows = _find_for_entity(jo, "multi.example")
        assert any(r.get("Type") == "A" and r.get("Response") == "203.0.113.10" and r.get("DNS Server") == "1.1.1.1" for r in rows)
        assert action_output.results.execution_state in (ExecutionState.COMPLETED, None)

    @set_metadata(
        parameters={
            "DNS Servers": "1.1.1.1",
            "Data Type": "ANY",
        }
    )
    def test_no_records_found_yields_false_and_message(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"DNS Servers": "1.1.1.1", "Data Type": "ANY"})
        _set_entities(monkeypatch, [("missing.example", "HOSTNAME")])
        _patch_dnspython_for_hostname(monkeypatch, {})

        Action.main()

        assert (action_output.results.output_message or "").strip() == "No records found"
        assert str(action_output.results.result_value).lower() == "false"
        assert action_output.results.json_output in (None, [], _jo_list(action_output.results.json_output))

    @set_metadata(
        parameters={
            "DNS Servers": "1.1.1.1",
            "Data Type": "ANY",
        }
    )
    def test_exceptions_in_dns_calls_are_caught_and_continue(self, action_output: MockActionOutput, monkeypatch) -> None:
        _patch_params(monkeypatch, {"DNS Servers": "1.1.1.1", "Data Type": "ANY"})
        _set_entities(monkeypatch, [("1.2.3.4", "ADDRESS"), ("err.example", "HOSTNAME")])

        class _ResBoom:
            def __init__(self, configure: bool = False) -> None:
                self.nameservers = []

            def resolve_address(self, ip: str) -> _FakePTRAnswer:
                raise RuntimeError("resolver boom")

        def _make_query(name: str, rdt: Any) -> Tuple[str, Any]:  # noqa: ANN001
            return (name, rdt)

        def _udp(query: Tuple[str, Any], server: str) -> _FakeDnsMsg:  # noqa: ANN001
            raise RuntimeError("udp boom")

        def _to_text(rt: Any) -> str:  # noqa: ANN001
            return "A"

        monkeypatch.setattr(Action.dns.resolver, "Resolver", _ResBoom, raising=True)
        monkeypatch.setattr(Action.dns.message, "make_query", _make_query, raising=True)
        monkeypatch.setattr(Action.dns.query, "udp", _udp, raising=True)
        monkeypatch.setattr(Action.dns.rdatatype, "to_text", _to_text, raising=True)

        Action.main()

        assert (action_output.results.output_message or "").strip() == "No records found"
        assert str(action_output.results.result_value).lower() == "false"
        assert _jo_list(action_output.results.json_output) in (None, [])
