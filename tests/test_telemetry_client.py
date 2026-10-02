from tinlance_agent_platform_sdk.client import AgentPlatform


class Sink:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def on_request(self, *, operation: str, request_id: str) -> None:
        self.events.append(("request", operation))

    def on_response(
        self,
        *,
        operation: str,
        request_id: str,
        status_code: int,
        elapsed_ms: float,
    ) -> None:
        self.events.append(("response", operation))

    def on_error(
        self,
        *,
        operation: str,
        request_id: str,
        error_type: str,
        status_code: int | None,
        elapsed_ms: float,
    ) -> None:
        self.events.append(("error", operation))


class BrokenSink:
    def on_request(self, **_: object) -> None:
        raise RuntimeError("telemetry failure")

    def on_response(self, **_: object) -> None:
        raise RuntimeError("telemetry failure")

    def on_error(self, **_: object) -> None:
        raise RuntimeError("telemetry failure")


def test_telemetry_hooks_are_non_authoritative() -> None:
    client = object.__new__(AgentPlatform)
    sink = Sink()
    client._telemetry = sink
    client._emit_telemetry_request("health", "req-1")
    client._emit_telemetry_response("health", "req-1", 200, 0.0)
    client._emit_telemetry_error("health", "req-1", "TransportError", None, 0.0)
    assert sink.events == [
        ("request", "health"),
        ("response", "health"),
        ("error", "health"),
    ]


def test_telemetry_failures_do_not_break_client() -> None:
    client = object.__new__(AgentPlatform)
    client._telemetry = BrokenSink()
    client._emit_telemetry_request("health", "req-1")
    client._emit_telemetry_response("health", "req-1", 200, 0.0)
    client._emit_telemetry_error("health", "req-1", "TransportError", None, 0.0)
