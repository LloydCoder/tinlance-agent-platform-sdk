"""Synchronous external client for the Tinlance Agent Platform API v1.1."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any, NoReturn
from uuid import UUID, uuid4

from .errors import (
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
from .models import Agent, ApprovalRef, Capability, Event, EvidenceRef, Health, Principal, Run

API_VERSION = "1.1"
MAX_REQUEST_BYTES = 1 * 1024 * 1024
_TRACEPARENT = re.compile(r"^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$")


def _normalize_request_id(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        raise ValueError("request_id must be non-empty, normalized, and at most 256 characters")
    if any(ord(character) < 0x21 or ord(character) > 0x7E for character in value):
        raise ValueError("request_id must contain printable ASCII only")
    return value


def _validate_traceparent(value: str) -> str:
    if not _TRACEPARENT.fullmatch(value):
        raise ValueError("traceparent must use W3C Trace Context format")
    trace_id = value[3:35]
    span_id = value[36:52]
    if trace_id == "0" * 32 or span_id == "0" * 16:
        raise ValueError("traceparent identifiers must not be all zero")
    return value


def _as_uuid(value: UUID | str, field: str) -> str:
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{field} must be a UUID") from exc


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


class _PrincipalResource:
    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def get(self, *, request_id: str | None = None) -> Principal:
        return Principal.from_payload(
            self._client._call("principal.get", {}, request_id=request_id, consequential=False)
        )


class _AgentsResource:
    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def list(self, *, request_id: str | None = None) -> tuple[Agent, ...]:
        payload = self._client._call("agents.list", {}, request_id=request_id, consequential=False)
        items = payload.get("agents")
        if not isinstance(items, list):
            raise PlatformError(
                "Platform returned an invalid agents payload", error_code="invalid_response"
            )
        if not all(isinstance(item, dict) for item in items):
            raise PlatformError("Platform returned an invalid agents payload", error_code="invalid_response")
        return tuple(Agent.from_payload(item) for item in items)


class _CapabilitiesResource:
    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def list(
        self, agent_id: UUID | str, *, request_id: str | None = None
    ) -> tuple[Capability, ...]:
        payload = self._client._call(
            "capabilities.list",
            {"agent_id": _as_uuid(agent_id, "agent_id")},
            request_id=request_id,
            consequential=False,
        )
        items = payload.get("capabilities")
        if not isinstance(items, list):
            raise PlatformError(
                "Platform returned an invalid capabilities payload", error_code="invalid_response"
            )
        if not all(isinstance(item, dict) for item in items):
            raise PlatformError(
                "Platform returned an invalid capabilities payload", error_code="invalid_response"
            )
        return tuple(Capability.from_payload(item) for item in items)


class _RunsResource:
    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def create(
        self,
        task_id: UUID | str,
        agent_id: UUID | str,
        intent: str,
        *,
        request_id: str | None = None,
    ) -> Run:
        return Run.from_payload(
            self._client._call(
                "runs.create",
                {
                    "task_id": _as_uuid(task_id, "task_id"),
                    "agent_id": _as_uuid(agent_id, "agent_id"),
                    "intent": _required_text(intent, "intent"),
                },
                request_id=request_id,
                consequential=True,
            )
        )

    def cancel(self, run_id: UUID | str, *, request_id: str | None = None) -> Run:
        return Run.from_payload(
            self._client._call(
                "runs.cancel",
                {"run_id": _as_uuid(run_id, "run_id")},
                request_id=request_id,
                consequential=True,
            )
        )

    def events(self, run_id: UUID | str, *, request_id: str | None = None) -> tuple[Event, ...]:
        payload = self._client._call(
            "runs.events",
            {"run_id": _as_uuid(run_id, "run_id")},
            request_id=request_id,
            consequential=False,
        )
        items = payload.get("events")
        if not isinstance(items, list):
            raise PlatformError(
                "Platform returned an invalid events payload", error_code="invalid_response"
            )
        if not all(isinstance(item, dict) for item in items):
            raise PlatformError("Platform returned an invalid events payload", error_code="invalid_response")
        return tuple(Event.from_payload(item) for item in items)

    def evidence(
        self, run_id: UUID | str, *, request_id: str | None = None
    ) -> tuple[EvidenceRef, ...]:
        payload = self._client._call(
            "runs.evidence",
            {"run_id": _as_uuid(run_id, "run_id")},
            request_id=request_id,
            consequential=False,
        )
        items = payload.get("evidence")
        if not isinstance(items, list):
            raise PlatformError(
                "Platform returned an invalid evidence payload", error_code="invalid_response"
            )
        if not all(isinstance(item, dict) for item in items):
            raise PlatformError(
                "Platform returned an invalid evidence payload", error_code="invalid_response"
            )
        return tuple(EvidenceRef.from_payload(item) for item in items)


class _ApprovalsResource:
    def __init__(self, client: AgentPlatform) -> None:
        self._client = client

    def request(
        self,
        run_id: UUID | str,
        action: str,
        resource: str,
        reason: str,
        *,
        request_id: str | None = None,
    ) -> ApprovalRef:
        return ApprovalRef.from_payload(
            self._client._call(
                "approvals.request",
                {
                    "run_id": _as_uuid(run_id, "run_id"),
                    "action": _required_text(action, "action"),
                    "resource": _required_text(resource, "resource"),
                    "reason": _required_text(reason, "reason"),
                },
                request_id=request_id,
                consequential=True,
            )
        )


class AgentPlatform:
    """Consumer-facing client for the versioned Platform operation gateway."""

    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str,
        tenant_id: str,
        subject_id: str,
        timeout: float = 10.0,
        api_version: str = API_VERSION,
        traceparent: str | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use HTTP or HTTPS")
        if not bearer_token or any(character.isspace() for character in bearer_token):
            raise ValueError("bearer_token must be non-empty and contain no whitespace")
        self._base_url = base_url.rstrip("/")
        self._bearer_token = bearer_token
        self._tenant_id = _required_text(tenant_id, "tenant_id")
        self._subject_id = _required_text(subject_id, "subject_id")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = timeout
        if api_version != API_VERSION:
            raise ValueError(f"SDK v0.1 supports Platform API version {API_VERSION} only")
        self._api_version = api_version
        self._traceparent = _validate_traceparent(traceparent) if traceparent is not None else None
        self.principal = _PrincipalResource(self)
        self.agents = _AgentsResource(self)
        self.capabilities = _CapabilitiesResource(self)
        self.runs = _RunsResource(self)
        self.approvals = _ApprovalsResource(self)

    def health(self, *, request_id: str | None = None) -> Health:
        return Health.from_payload(
            self._call("health", {}, request_id=request_id, consequential=False)
        )

    def _call(
        self,
        operation: str,
        payload: dict[str, Any],
        *,
        request_id: str | None,
        consequential: bool,
    ) -> dict[str, Any]:
        rid = _normalize_request_id(request_id or str(uuid4()))
        body = {
            "tenant_id": self._tenant_id,
            "subject_id": self._subject_id,
            "operation": operation,
            "payload": payload,
        }
        raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(raw) > MAX_REQUEST_BYTES:
            raise RequestTooLargeError(
                "request exceeds the Platform 1 MiB request-body limit",
                status_code=413,
                error_code="request_too_large",
            )
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._bearer_token}",
            "X-Tinlance-API-Version": self._api_version,
            "X-Request-ID": rid,
        }
        if consequential:
            headers["Idempotency-Key"] = rid
        if self._traceparent is not None:
            headers["traceparent"] = self._traceparent
        request = urllib.request.Request(
            f"{self._base_url}/v1/agent-platform",
            data=raw,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                response_body = self._decode_response(response.read())
        except urllib.error.HTTPError as exc:
            self._raise_http_error(exc)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise TransportError("request to Tinlance Agent Platform failed") from exc
        if not isinstance(response_body, dict):
            raise PlatformError(
                "Platform returned a non-object response",
                status_code=200,
                error_code="invalid_response",
            )
        status = response_body.get("status")
        if status not in {"ok", "accepted"}:
            raise PlatformError(
                "Platform returned an invalid success envelope",
                status_code=200,
                error_code="invalid_response",
            )
        payload_value = response_body.get("payload", {})
        if not isinstance(payload_value, dict):
            raise PlatformError(
                "Platform returned an invalid payload",
                status_code=200,
                error_code="invalid_response",
            )
        return payload_value

    @staticmethod
    def _decode_response(raw: bytes) -> Any:
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PlatformError(
                "Platform returned invalid JSON", error_code="invalid_response"
            ) from exc

    @staticmethod
    def _raise_http_error(error: urllib.error.HTTPError) -> NoReturn:
        try:
            body = json.loads(error.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = {}
        code = body.get("error") if isinstance(body, dict) else None
        message = f"Platform request failed with HTTP {error.code}"
        if isinstance(code, str):
            message = f"{message}: {code}"
        mapping: dict[int, type[PlatformError]] = {
            400: InvalidRequestError,
            401: AuthenticationError,
            403: PermissionError,
            409: IdempotencyConflictError,
            413: RequestTooLargeError,
            415: UnsupportedMediaTypeError,
            426: ApiVersionError,
            500: PlatformError,
        }
        error_type = mapping.get(error.code, PlatformError)
        raise error_type(message, status_code=error.code, error_code=code) from error
