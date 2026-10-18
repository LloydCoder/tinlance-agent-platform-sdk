import json

import pytest

from tinlance_agent_platform_sdk.events import CloudEvent


def make_event(**overrides):
    values = {
        "id": "event-001",
        "source": "https://tinlance.com/platform/runs",
        "type": "com.tinlance.execution.completed.v1",
        "time": "2026-10-18T04:00:00Z",
        "tenantid": "tenant-a",
        "executionid": "run-001",
        "traceid": "4bf92f3577b34da6a3ce929d0e0e4736",
        "correlationid": "workflow-001",
        "data": {"state": "succeeded"},
    }
    values.update(overrides)
    return CloudEvent(**values)


def test_cloud_event_serializes_cloud_events_names_and_context() -> None:
    payload = make_event(subject="run-001", spanid="00f067aa0ba902b7").as_payload()
    assert payload["specversion"] == "1.0"
    assert payload["datacontenttype"] == "application/json"
    assert payload["tenantid"] == "tenant-a"
    assert payload["traceid"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert "tenant_id" not in payload
    assert "data_content_type" not in payload
    assert json.loads(make_event().to_json())["data"] == {"state": "succeeded"}


@pytest.mark.parametrize(
    "overrides",
    [
        {"traceid": "0" * 32},
        {"traceid": "bad"},
        {"spanid": "0" * 16},
        {"spanid": "bad"},
        {"time": "2026-10-18T04:00:00"},
        {"source": "not a URI"},
        {"source": "https://"},
        {"source": "https://user:password@example.test/events"},
        {"dataschema": "/relative/schema.json"},
        {"dataschema": "https://"},
        {"tenantid": " tenant-a"},
        {"datacontenttype": "text/plain"},
        {"specversion": "2.0"},
        {"data": {"nan": float("nan")}},
    ],
)
def test_cloud_event_rejects_invalid_envelope(overrides) -> None:
    with pytest.raises(ValueError):
        make_event(**overrides)


def test_cloud_event_does_not_expose_mutable_input_mapping() -> None:
    data = {"state": "succeeded"}
    event = make_event(data=data)
    data["state"] = "failed"
    assert event.as_payload()["data"]["state"] == "succeeded"


def test_nested_event_payload_is_immutable() -> None:
    data = {"nested": {"state": "succeeded"}}
    event = make_event(data=data)
    data["nested"]["state"] = "failed"
    with pytest.raises(TypeError):
        event.data["nested"]["state"] = "mutated"
    assert event.as_payload()["data"]["nested"]["state"] == "succeeded"
