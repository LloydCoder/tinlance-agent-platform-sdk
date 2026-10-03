from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from uuid import uuid4

from tinlance_agent_platform_sdk import AgentPlatform, ToolInvocation

TENANT = "tenant-conformance"
SUBJECT = "principal-conformance"
TOKEN = "opaque-conformance-token"
AGENT = uuid4()
TASK = uuid4()
RUN = uuid4()
APPROVAL = uuid4()
EXECUTION = uuid4()
EVENT = uuid4()
EVIDENCE = uuid4()


class ConformanceServer:
    def __init__(self) -> None:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers["Content-Length"])
                body = json.loads(self.rfile.read(length))
                parent.requests.append(
                    (body, {k.lower(): v for k, v in self.headers.items()})
                )
                response = parent.response(body["operation"])
                raw = json.dumps(response).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("X-Tinlance-API-Version", "1.1")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, _format: str, *_args: object) -> None:
                return

        self.requests: list[tuple[dict[str, object], dict[str, str]]] = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def response(self, operation: str) -> dict[str, object]:
        payloads: dict[str, object] = {
            "health": {"ready": True},
            "principal.get": {"user_id": SUBJECT},
            "agents.list": {
                "agents": [
                    {
                        "agent_id": str(AGENT),
                        "name": "conformance",
                        "version": "1.0.0",
                    }
                ]
            },
            "capabilities.list": {
                "capabilities": [{"capability_id": "repository.read"}]
            },
            "runs.create": {
                "run_id": str(RUN),
                "task_id": str(TASK),
                "state": "running",
                "agent_id": str(AGENT),
            },
            "runs.cancel": {
                "run_id": str(RUN),
                "task_id": str(TASK),
                "state": "cancelled",
                "agent_id": str(AGENT),
            },
            "approvals.request": {"approval_id": str(APPROVAL)},
            "approvals.decide": {
                "approval_id": str(APPROVAL),
                "state": "approved",
            },
            "tools.execute": {
                "execution_id": str(EXECUTION),
                "state": "completed",
                "output": "ok",
                "evidence_ids": [str(EVIDENCE)],
                "audit_event_ids": [str(EVENT)],
                "error_code": None,
                "retryable": False,
            },
            "executions.get": {
                "execution_id": str(EXECUTION),
                "state": "completed",
                "output": "ok",
                "evidence_ids": [str(EVIDENCE)],
                "audit_event_ids": [str(EVENT)],
                "error_code": None,
                "retryable": False,
            },
            "runs.events": {
                "events": [
                    {
                        "event_id": str(EVENT),
                        "event_type": "run.created",
                        "occurred_at": "2026-10-03T00:00:00+00:00",
                        "request_id": "r",
                        "correlation_id": "r",
                        "workspace_id": TENANT,
                        "task_id": str(TASK),
                        "agent_id": str(AGENT),
                        "platform_run_id": str(RUN),
                        "payload": {},
                    }
                ]
            },
            "runs.evidence": {
                "evidence": [{"evidence_id": str(EVIDENCE)}]
            },
        }
        expected = {
            "health": "ok",
            "principal.get": "ok",
            "agents.list": "ok",
            "capabilities.list": "ok",
            "runs.create": "accepted",
            "runs.cancel": "accepted",
            "approvals.request": "accepted",
            "approvals.decide": "accepted",
            "tools.execute": "accepted",
            "executions.get": "ok",
            "runs.events": "ok",
            "runs.evidence": "ok",
        }
        return {"status": expected[operation], "payload": payloads[operation]}

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def client(server: ConformanceServer) -> AgentPlatform:
    return AgentPlatform(
        base_url=f"http://127.0.0.1:{server.server.server_address[1]}",
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
        allow_insecure_http=True,
    )


def test_m21_1_all_public_operations_round_trip() -> None:
    server = ConformanceServer()
    try:
        sdk = client(server)
        assert sdk.health().ready
        assert sdk.principal.get().user_id == SUBJECT
        assert sdk.agents.list()[0].agent_id == AGENT
        assert sdk.capabilities.list(AGENT)[0].capability_id == "repository.read"
        assert sdk.runs.create(TASK, AGENT, "conformance").run_id == RUN
        assert sdk.runs.cancel(RUN).state == "cancelled"
        approval = sdk.approvals.request(
            RUN, "test.action", "resource", "conformance"
        )
        assert approval.approval_id == APPROVAL
        assert sdk.approvals.decide(APPROVAL, True).state == "approved"
        invocation = ToolInvocation(
            "repository.read", "repository.read", "inspect", "repo:x", {}
        )
        assert sdk.tools.execute(RUN, AGENT, invocation).execution_id == EXECUTION
        assert sdk.executions.get(EXECUTION).execution_id == EXECUTION
        assert sdk.runs.events(RUN)[0].event_id == EVENT
        assert sdk.runs.evidence(RUN)[0].evidence_id == EVIDENCE
        assert [body["operation"] for body, _ in server.requests] == [
            "health",
            "principal.get",
            "agents.list",
            "capabilities.list",
            "runs.create",
            "runs.cancel",
            "approvals.request",
            "approvals.decide",
            "tools.execute",
            "executions.get",
            "runs.events",
            "runs.evidence",
        ]
    finally:
        server.close()


def test_m21_1_r10_wire_contract_is_explicit() -> None:
    server = ConformanceServer()
    try:
        sdk = client(server)
        invocation = ToolInvocation(
            "repository.read",
            "repository.read",
            "inspect",
            "repo:x",
            {"depth": 1},
        )
        sdk.tools.execute(
            RUN,
            AGENT,
            invocation,
            capability_version="2",
            tool_version="7",
            requested_timeout_seconds=12,
            requested_tool_calls=3,
            risk="high",
            reversibility="irreversible",
            data_class="restricted",
            blast_radius="tenant",
            sandbox_required=True,
            evidence_required=True,
            request_id="r10-request",
            idempotency_key="r10-key",
        )
        body, headers = server.requests[-1]
        assert body == {
            "tenant_id": TENANT,
            "subject_id": SUBJECT,
            "operation": "tools.execute",
            "payload": {
                "contract_version": "governed-execution.v1",
                "run_id": str(RUN),
                "agent_id": str(AGENT),
                "capability_id": "repository.read",
                "capability_version": "2",
                "tool_name": "repository.read",
                "tool_version": "7",
                "action": "inspect",
                "resource": "repo:x",
                "input": {"depth": 1},
                "requested_timeout_seconds": 12,
                "requested_tool_calls": 3,
                "risk": "high",
                "reversibility": "irreversible",
                "data_class": "restricted",
                "blast_radius": "tenant",
                "sandbox_required": True,
                "evidence_required": True,
            },
        }
        assert headers["x-tinlance-api-version"] == "1.1"
        assert headers["x-request-id"] == "r10-request"
        assert headers["idempotency-key"] == "r10-key"
    finally:
        server.close()


def test_m21_1_consequential_identity_is_stable_and_reads_are_not_idempotent() -> None:
    server = ConformanceServer()
    try:
        sdk = client(server)
        sdk.runs.create(TASK, AGENT, "same intent", request_id="stable-request")
        sdk.health(request_id="read-request")
        consequential_headers = server.requests[0][1]
        read_headers = server.requests[1][1]
        assert consequential_headers["x-request-id"] == "stable-request"
        assert consequential_headers["idempotency-key"] == "stable-request"
        assert read_headers["x-request-id"] == "read-request"
        assert "idempotency-key" not in read_headers
    finally:
        server.close()
