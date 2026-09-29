"""Validated configuration for the external Tinlance Agent Platform SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from .client import API_VERSION, MAX_RESPONSE_BYTES, _normalize_request_id, _validate_traceparent


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Immutable SDK configuration; credentials remain opaque to the SDK."""

    base_url: str
    bearer_token: str
    tenant_id: str
    subject_id: str
    timeout: float = 10.0
    api_version: str = API_VERSION
    traceparent: str | None = None
    allow_insecure_http: bool = False
    max_response_bytes: int = MAX_RESPONSE_BYTES
    user_agent: str = "tinlance-agent-platform-sdk/0.1.0"

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an absolute HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("base_url must not contain userinfo")
        if parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain query or fragment components")
        if parsed.scheme != "https" and not self.allow_insecure_http:
            raise ValueError("base_url must use HTTPS unless allow_insecure_http=True")
        if not self.bearer_token or any(character.isspace() for character in self.bearer_token):
            raise ValueError("bearer_token must be non-empty and contain no whitespace")
        if not self.tenant_id.strip() or not self.subject_id.strip():
            raise ValueError("tenant_id and subject_id are required")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.api_version != API_VERSION:
            raise ValueError(f"SDK v0.1 supports Platform API version {API_VERSION} only")
        if self.max_response_bytes <= 0:
            raise ValueError("max_response_bytes must be positive")
        if not self.user_agent.strip():
            raise ValueError("user_agent must be non-empty")
        if self.traceparent is not None:
            _validate_traceparent(self.traceparent)

    def normalized_request_id(self, value: str) -> str:
        return _normalize_request_id(value)

    def as_client_kwargs(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "bearer_token": self.bearer_token,
            "tenant_id": self.tenant_id,
            "subject_id": self.subject_id,
            "timeout": self.timeout,
            "api_version": self.api_version,
            "traceparent": self.traceparent,
            "allow_insecure_http": self.allow_insecure_http,
            "max_response_bytes": self.max_response_bytes,
            "user_agent": self.user_agent,
        }
