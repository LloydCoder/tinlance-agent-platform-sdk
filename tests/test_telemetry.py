from tinlance_agent_platform_sdk.telemetry import safe_attributes


def test_telemetry_attributes_are_allow_listed() -> None:
    attrs = safe_attributes(
        operation="runs.create",
        request_id="req-1",
        status_code=200,
        elapsed_ms=12.5,
    )
    assert attrs == {
        "tinlance.operation": "runs.create",
        "tinlance.request_id": "req-1",
        "http.status_code": 200,
        "tinlance.elapsed_ms": 12.5,
    }
    assert "authorization" not in {key.lower() for key in attrs}
    assert "payload" not in {key.lower() for key in attrs}
