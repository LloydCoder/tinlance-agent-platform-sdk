from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4

import pytest

from tinlance_agent_platform_sdk import (
    AgentPlatform,
    ApiVersionError,
    AuthenticationError,
    IdempotencyConflictError,
    InvalidRequestError,
    PermissionError,
    PlatformError,
    RequestTooLargeError,
    TransportError,
    UnsupportedMediaTypeError,
)

TENANT = "tenant-a"
SUBJECT = "user-a"
TOKEN = "opaque-token"
AGENT_ID = uuid4()
TASK_ID = uuid4()
RUN_ID = uuid4()
APPROVAL_ID = uuid4()
EVENT_ID = uuid4()
EVIDENCE_ID = uuid4()
EXECUTION_ID = uuid4()


class FakePlatform:
    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []
        self.headers: list[dict[str, str]] = []
        self.responses: dict[str, tuple[int, dict[str, object]]] = {}
        self.raw_responses: dict[str, tuple[int, bytes]] = {}
        self.response_versions: dict[str, str] = {}
        self.response_content_types: dict[str, str] = {}
        self.redirect_locations: dict[str, str] = {}
        self.server = self._server()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def _server(self) -> ThreadingHTTPServer:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length))
                parent.requests.append(body)
                parent.headers.append({key.lower(): value for key, value in self.headers.items()})
                operation = body["operation"]
                if not isinstance(operation, str):
                    raise AssertionError("operation must be text")
                if operation in parent.raw_responses:
                    status, raw = parent.raw_responses[operation]
                else:
                    status, response = parent.responses.get(operation, parent._default(operation))
                    raw = json.dumps(response).encode()
                self.send_response(status)
                self.send_header(
                    "Content-Type", parent.response_content_types.get(operation, "application/json")
                )
                self.send_header(
                    "X-Tinlance-API-Version", parent.response_versions.get(operation, "1.1")
                )
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, _format: str, *_args: object) -> None:
                return

        return ThreadingHTTPServer(("127.0.0.1", 0), Handler)

    def _default(self, operation: str) -> tuple[int, dict[str, object]]:
        if operation == "health":
            return 200, {"status": "ok", "payload": {"ready": True}}
        if operation == "principal.get":
            return 200, {"status": "ok", "payload": {"user_id": SUBJECT}}
        if operation == "agents.list":
            return 200, {
                "status": "ok",
                "payload": {
                    "agents": [
                        {"agent_id": str(AGENT_ID), "name": "security-agent", "version": "1.0.0"}
                    ]
                },
            }
        if operation == "capabilities.list":
            return 200, {
                "status": "ok",
                "payload": {"capabilities": [{"capability_id": "repository.read"}]},
            }
        if operation == "runs.create":
            return 200, {
                "status": "accepted",
                "payload": {
                    "run_id": str(RUN_ID),
                    "task_id": str(TASK_ID),
                    "state": "running",
                    "agent_id": str(AGENT_ID),
                },
            }
        if operation == "runs.cancel":
            return 200, {
                "status": "accepted",
                "payload": {
                    "run_id": str(RUN_ID),
                    "task_id": str(TASK_ID),
                    "state": "cancelled",
                    "agent_id": str(AGENT_ID),
                },
            }
        if operation == "approvals.request":
            return 200, {"status": "accepted", "payload": {"approval_id": str(APPROVAL_ID)}}
        if operation == "runs.events":
            return 200, {
                "status": "ok",
                "payload": {
                    "events": [
                        {
                            "event_id": str(EVENT_ID),
                            "event_type": "run.created",
                            "occurred_at": "2026-09-29T09:00:00+00:00",
                            "request_id": "request-id",
                            "correlation_id": "request-id",
                            "workspace_id": TENANT,
                            "task_id": None,
                            "agent_id": None,
                            "platform_run_id": str(RUN_ID),
                            "payload": {"task_id": str(TASK_ID)},
                        }
                    ]
                },
            }
        if operation == "runs.evidence":
            return 200, {
                "status": "ok",
                "payload": {"evidence": [{"evidence_id": str(EVIDENCE_ID)}]},
            }
        if operation == "approvals.decide":
            return 200, {
                "status": "accepted",
                "payload": {"approval_id": str(APPROVAL_ID), "state": "approved"},
            }
        if operation == "tools.execute":
            return 200, {
                "status": "accepted",
                "payload": {
                    "execution_id": str(EXECUTION_ID),
                    "state": "completed",
                    "output": "ok",
                    "evidence_ids": [str(EVIDENCE_ID)],
                    "audit_event_ids": [str(EVENT_ID)],
                    "error_code": None,
                    "retryable": False,
                },
            }
        if operation == "executions.get":
            return 200, {
                "status": "ok",
                "payload": {
                    "execution_id": str(EXECUTION_ID),
                    "state": "completed",
                    "output": "ok",
                    "evidence_ids": [str(EVIDENCE_ID)],
                    "audit_event_ids": [str(EVENT_ID)],
                    "error_code": None,
                    "retryable": False,
                },
            }
        return 400, {"error": "invalid_request"}

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


@pytest.fixture
def fake() -> FakePlatform:
    server = FakePlatform()
    yield server
    server.close()


def make_client(fake: FakePlatform) -> AgentPlatform:
    return AgentPlatform(
        base_url=f"http://127.0.0.1:{fake.server.server_address[1]}",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
    )


def test_v1_1_public_surface(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    assert sdk.health().ready is True
    assert sdk.principal.get().user_id == SUBJECT
    assert sdk.agents.list()[0].agent_id == AGENT_ID
    assert sdk.capabilities.list(AGENT_ID)[0].capability_id == "repository.read"
    assert sdk.runs.create(TASK_ID, AGENT_ID, "inspect repository").run_id == RUN_ID
    assert sdk.runs.cancel(RUN_ID).state == "cancelled"
    assert (
        sdk.approvals.request(
            RUN_ID, "security.scan", "repo:example", "governed approval required"
        ).approval_id
        == APPROVAL_ID
    )
    assert sdk.runs.events(RUN_ID)[0].event_id == EVENT_ID
    assert sdk.runs.evidence(RUN_ID)[0].evidence_id == EVIDENCE_ID


def test_wire_contract_and_correlation_headers(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    request_id = str(uuid4())
    sdk.runs.create(TASK_ID, AGENT_ID, "inspect repository", request_id=request_id)
    body = fake.requests[-1]
    headers = fake.headers[-1]
    assert body == {
        "tenant_id": TENANT,
        "subject_id": SUBJECT,
        "operation": "runs.create",
        "payload": {
            "task_id": str(TASK_ID),
            "agent_id": str(AGENT_ID),
            "intent": "inspect repository",
        },
    }
    assert headers["authorization"] == f"Bearer {TOKEN}"
    assert headers["x-tinlance-api-version"] == "1.1"
    assert headers["x-request-id"] == request_id
    assert headers["idempotency-key"] == request_id
    assert "tenant" not in headers["authorization"].lower()


def test_read_operation_does_not_send_idempotency_key(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    sdk.health()
    assert "idempotency-key" not in fake.headers[-1]


def test_traceparent_is_propagated(fake: FakePlatform) -> None:
    sdk = AgentPlatform(
        base_url=f"http://127.0.0.1:{fake.server.server_address[1]}",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
        traceparent="00-11111111111111111111111111111111-2222222222222222-01",
    )
    sdk.health()
    assert fake.headers[-1]["traceparent"] == (
        "00-11111111111111111111111111111111-2222222222222222-01"
    )


@pytest.mark.parametrize(
    ("status", "error_code", "error_type"),
    [
        (400, "invalid_request", InvalidRequestError),
        (401, "unauthorized", AuthenticationError),
        (403, "forbidden", PermissionError),
        (409, "idempotency_conflict", IdempotencyConflictError),
        (413, "request_too_large", RequestTooLargeError),
        (415, "json_required", UnsupportedMediaTypeError),
        (426, "api_version_required", ApiVersionError),
        (500, "platform_error", PlatformError),
    ],
)
def test_error_mapping(
    fake: FakePlatform, status: int, error_code: str, error_type: type[Exception]
) -> None:
    fake.responses["health"] = (status, {"error": error_code})
    with pytest.raises(error_type) as exc_info:
        make_client(fake).health()
    error = exc_info.value
    assert error.status_code == status
    assert error.error_code == error_code
    assert TOKEN not in str(error)


def test_consequential_request_ids_are_reused_only_when_supplied(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    request_id = str(uuid4())
    sdk.runs.create(TASK_ID, AGENT_ID, "inspect repository", request_id=request_id)
    first = fake.headers[-1]["x-request-id"]
    sdk.runs.create(TASK_ID, AGENT_ID, "inspect repository")
    second = fake.headers[-1]["x-request-id"]
    assert first == request_id
    assert second != first


def test_request_id_validation() -> None:
    sdk = AgentPlatform(
        base_url="https://example.com",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
    )
    with pytest.raises(ValueError):
        sdk.health(request_id=" ")
    with pytest.raises(ValueError):
        sdk.health(request_id="x" * 257)
    with pytest.raises(ValueError):
        sdk.health(request_id="contains\nnewline")


def test_https_is_required_by_default() -> None:
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="http://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
        )

    client = AgentPlatform(
        base_url="http://example.com",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
    )
    assert client is not None


def test_client_configuration_validation() -> None:
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="not-a-url", bearer_token=TOKEN, tenant_id=TENANT, subject_id=SUBJECT
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            timeout=0,
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            traceparent="invalid",
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            api_version="9.9",
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://user:pass@example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com?token=secret",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
        )


def test_client_input_validation(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    with pytest.raises(ValueError):
        sdk.runs.create("not-a-uuid", AGENT_ID, "intent")
    with pytest.raises(ValueError):
        sdk.runs.create(TASK_ID, AGENT_ID, "")
    with pytest.raises(ValueError):
        sdk.capabilities.list("not-a-uuid")


def test_malformed_success_payload_is_rejected(fake: FakePlatform) -> None:
    fake.responses["health"] = (200, {"status": "ok", "payload": {"ready": "yes"}})
    with pytest.raises(ValueError):
        make_client(fake).health()


def test_invalid_traceparent_is_rejected() -> None:
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            traceparent="00-" + "0" * 32 + "-2222222222222222-01",
        )
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token=TOKEN,
            tenant_id=TENANT,
            subject_id=SUBJECT,
            traceparent="00-11111111111111111111111111111111-" + "0" * 16 + "-01",
        )


@pytest.mark.parametrize(
    ("operation", "method"),
    [
        ("agents.list", "agents"),
        ("capabilities.list", "capabilities"),
        ("runs.events", "events"),
        ("runs.evidence", "evidence"),
    ],
)
def test_malformed_collections_are_rejected(
    fake: FakePlatform, operation: str, method: str
) -> None:
    fake.responses[operation] = (
        200,
        {
            "status": "ok",
            "payload": {
                "agents": ["bad"],
                "capabilities": ["bad"],
                "events": ["bad"],
                "evidence": ["bad"],
            },
        },
    )
    sdk = make_client(fake)
    with pytest.raises(PlatformError):
        if method == "agents":
            sdk.agents.list()
        elif method == "capabilities":
            sdk.capabilities.list(AGENT_ID)
        elif method == "events":
            sdk.runs.events(RUN_ID)
        else:
            sdk.runs.evidence(RUN_ID)


def test_request_body_size_is_enforced(fake: FakePlatform) -> None:
    sdk = make_client(fake)
    with pytest.raises(RequestTooLargeError):
        sdk.runs.create(TASK_ID, AGENT_ID, "x" * (1024 * 1024))


def test_malformed_success_envelopes_are_rejected(fake: FakePlatform) -> None:
    fake.raw_responses["health"] = (200, b"not-json")
    with pytest.raises(PlatformError):
        make_client(fake).health()

    fake.responses["health"] = (200, [])
    with pytest.raises(PlatformError):
        make_client(fake).health()

    fake.responses["health"] = (200, {"status": "unexpected", "payload": {}})
    with pytest.raises(PlatformError):
        make_client(fake).health()

    fake.responses["health"] = (200, {"status": "ok", "payload": []})
    with pytest.raises(PlatformError):
        make_client(fake).health()


def test_unknown_http_status_maps_to_platform_error(fake: FakePlatform) -> None:
    fake.responses["health"] = (418, {"error": "teapot"})
    with pytest.raises(PlatformError) as exc_info:
        make_client(fake).health()
    assert exc_info.value.status_code == 418
    assert exc_info.value.error_code == "teapot"


def test_transport_failure_is_typed() -> None:
    sdk = AgentPlatform(
        base_url="http://127.0.0.1:1",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
        timeout=0.1,
    )
    with pytest.raises(TransportError):
        sdk.health()


def test_bearer_configuration_rejects_invalid_credentials() -> None:
    with pytest.raises(ValueError):
        AgentPlatform(
            base_url="https://example.com",
            bearer_token="bad token",
            tenant_id=TENANT,
            subject_id=SUBJECT,
        )


def test_model_invalid_payloads_are_rejected(fake: FakePlatform) -> None:
    fake.responses["agents.list"] = (
        200,
        {
            "status": "ok",
            "payload": {"agents": [{"agent_id": "bad", "name": "x", "version": "1.0.0"}]},
        },
    )
    with pytest.raises(ValueError):
        make_client(fake).agents.list()

    fake.responses["runs.create"] = (
        200,
        {
            "status": "accepted",
            "payload": {
                "run_id": str(RUN_ID),
                "task_id": str(TASK_ID),
                "agent_id": str(AGENT_ID),
                "state": "not-a-state",
            },
        },
    )
    with pytest.raises(ValueError):
        make_client(fake).runs.create(TASK_ID, AGENT_ID, "intent")


def test_response_api_version_is_verified(fake: FakePlatform) -> None:
    fake.response_versions["health"] = "1.0"
    with pytest.raises(ApiVersionError) as exc_info:
        make_client(fake).health()
    assert exc_info.value.error_code == "api_version_mismatch"


def test_response_content_type_is_verified(fake: FakePlatform) -> None:
    fake.response_content_types["health"] = "text/html"
    with pytest.raises(UnsupportedMediaTypeError) as exc_info:
        make_client(fake).health()
    assert exc_info.value.error_code == "invalid_response_content_type"


@pytest.mark.parametrize("operation", ["health", "runs.create"])
def test_operation_specific_success_status_is_verified(fake: FakePlatform, operation: str) -> None:
    fake.responses[operation] = (
        200,
        {
            "status": "accepted" if operation == "health" else "ok",
            "payload": (
                {"ready": True}
                if operation == "health"
                else {
                    "run_id": str(RUN_ID),
                    "task_id": str(TASK_ID),
                    "state": "running",
                    "agent_id": str(AGENT_ID),
                },
            ),
        },
    )
    with pytest.raises(PlatformError) as exc_info:
        if operation == "health":
            make_client(fake).health()
        else:
            make_client(fake).runs.create(TASK_ID, AGENT_ID, "intent")
    assert exc_info.value.error_code == "invalid_response"


def test_oversized_response_is_rejected(fake: FakePlatform) -> None:
    sdk = AgentPlatform(
        base_url=f"http://127.0.0.1:{fake.server.server_address[1]}",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
        max_response_bytes=32,
    )
    fake.raw_responses["health"] = (200, b'{"status":"ok","payload":{"ready":true}}')
    with pytest.raises(RequestTooLargeError) as exc_info:
        sdk.health()
    assert exc_info.value.error_code == "response_too_large"


def test_redirects_are_disabled(fake: FakePlatform) -> None:
    fake.responses["health"] = (302, {"error": "redirect"})
    fake.redirect_locations["health"] = "http://127.0.0.1:9/"
    with pytest.raises(TransportError, match="redirects are disabled"):
        make_client(fake).health()


def test_malformed_http_error_json_fails_closed(fake: FakePlatform) -> None:
    fake.raw_responses["health"] = (400, b'{"unexpected":"shape"}')
    with pytest.raises(PlatformError) as exc_info:
        make_client(fake).health()
    assert exc_info.value.error_code == "invalid_response"

    fake.raw_responses["health"] = (400, b"not-json")
    with pytest.raises(PlatformError) as exc_info:
        make_client(fake).health()
    assert exc_info.value.error_code == "invalid_response"


def test_oversized_http_error_is_rejected(fake: FakePlatform) -> None:
    sdk = AgentPlatform(
        base_url=f"http://127.0.0.1:{fake.server.server_address[1]}",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
        max_response_bytes=32,
    )
    fake.raw_responses["health"] = (400, b'{"error":"' + b"x" * 64 + b'"}')
    with pytest.raises(RequestTooLargeError) as exc_info:
        sdk.health()
    assert exc_info.value.error_code == "response_too_large"


def test_r10_execution_and_approval_contract(fake: FakePlatform) -> None:
    from tinlance_agent_platform_sdk import ToolInvocation

    sdk = make_client(fake)
    key = str(uuid4())
    decision = sdk.approvals.decide(
        APPROVAL_ID, True, request_id=str(uuid4()), idempotency_key=key
    )
    assert decision.approval_id == APPROVAL_ID
    invocation = ToolInvocation(
        "reference.echo", "repository.read", "read", "repo:example", {"path": "README.md"}
    )
    execution = sdk.tools.execute(
        RUN_ID,
        AGENT_ID,
        invocation,
        capability_version="1",
        tool_version="1",
        risk="high",
        approval_id=APPROVAL_ID,
        request_id=str(uuid4()),
        idempotency_key=key + "-exec",
    )
    assert execution.execution_id == EXECUTION_ID
    assert sdk.executions.get(EXECUTION_ID).state == "completed"
    assert fake.requests[-3]["operation"] == "approvals.decide"
    assert fake.headers[-3]["idempotency-key"] == key
    assert fake.requests[-2]["operation"] == "tools.execute"
    assert fake.headers[-2]["idempotency-key"] == key + "-exec"
