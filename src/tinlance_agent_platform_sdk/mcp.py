"""Declarative MCP integration metadata.

This module describes MCP peers and tool invocations without implementing an MCP
runtime. Authentication material and execution authority remain outside the SDK.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlparse

MCPTransport = Literal["streamable_http", "stdio"]
MCPProtocolVersion = Literal["2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26"]
_SUPPORTED_PROTOCOL_VERSIONS = frozenset(
    {"2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26"}
)
_SENSITIVE_METADATA_KEY = re.compile(
    r"(?:^|[_-])(authorization|token|secret|password|credential|api[_-]?key|private[_-]?key)(?:$|[_-])",
    re.IGNORECASE,
)
_SENSITIVE_METADATA_VALUE = re.compile(
    r"(?i)(?:\bbearer\s+\S+|(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})\b)"
)


def _validate_metadata(metadata: tuple[tuple[str, str], ...]) -> None:
    seen: set[str] = set()
    for key, value in metadata:
        if not isinstance(key, str) or not key.strip() or key != key.strip():
            raise ValueError("MCP metadata keys must be normalized non-empty strings")
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError("MCP metadata values must be normalized non-empty strings")
        normalized = key.casefold()
        if normalized in seen:
            raise ValueError("MCP metadata keys must be unique")
        seen.add(normalized)
        if _SENSITIVE_METADATA_KEY.search(key) or _SENSITIVE_METADATA_VALUE.search(value):
            raise ValueError("credential-shaped metadata is not permitted")


def _validate_http_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or not parsed.netloc:
        raise ValueError("MCP HTTP endpoint must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("MCP endpoint must not embed credentials")
    if parsed.fragment or parsed.query:
        raise ValueError("MCP endpoint must not contain query or fragment data")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("MCP endpoint port is invalid") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("MCP endpoint port is invalid")
    hostname = parsed.hostname.rstrip(".").lower()
    loopback = hostname == "localhost" or hostname.endswith(".localhost")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global and not address.is_loopback:
        raise ValueError("MCP endpoint must not use a non-public IP address")
    if parsed.scheme == "http" and not (
        loopback or (address is not None and address.is_loopback)
    ):
        raise ValueError("cleartext MCP is allowed only for loopback development")


@dataclass(frozen=True, slots=True)
class MCPTransportSpec:
    kind: MCPTransport
    endpoint: str | None = None
    protocol_versions: tuple[MCPProtocolVersion, ...] = ("2026-07-28", "2025-11-25")

    def __post_init__(self) -> None:
        if self.kind not in {"streamable_http", "stdio"}:
            raise ValueError("unsupported MCP transport kind")
        if not self.protocol_versions or any(
            version not in _SUPPORTED_PROTOCOL_VERSIONS for version in self.protocol_versions
        ):
            raise ValueError("MCP transport declares an unsupported protocol version")
        if len(set(self.protocol_versions)) != len(self.protocol_versions):
            raise ValueError("MCP protocol versions must be unique")
        if self.kind == "streamable_http":
            if self.endpoint is None:
                raise ValueError("streamable_http requires an endpoint")
            _validate_http_endpoint(self.endpoint)
        elif self.endpoint is not None:
            raise ValueError("stdio transport must not contain an HTTP endpoint")
        if not self.protocol_versions:
            raise ValueError("at least one MCP protocol version is required")

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "kind": self.kind,
            "protocol_versions": list(self.protocol_versions),
        }
        if self.endpoint is not None:
            payload["endpoint"] = self.endpoint
        return payload


@dataclass(frozen=True, slots=True)
class MCPAuthMetadata:
    """Authentication metadata only; never stores bearer tokens or client secrets."""

    scheme: str
    issuer: str | None = None
    audience: str | None = None
    scopes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.scheme.strip():
            raise ValueError("MCP auth scheme is required")
        if self.issuer is not None and not self.issuer.strip():
            raise ValueError("MCP issuer must be non-empty when supplied")
        if self.audience is not None and not self.audience.strip():
            raise ValueError("MCP audience must be non-empty when supplied")
        if any(not scope.strip() for scope in self.scopes):
            raise ValueError("MCP scopes must be non-empty")

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"scheme": self.scheme}
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.audience is not None:
            payload["audience"] = self.audience
        if self.scopes:
            payload["scopes"] = list(self.scopes)
        return payload


@dataclass(frozen=True, slots=True)
class MCPServerSpec:
    name: str
    version: str
    transport: MCPTransportSpec
    auth: MCPAuthMetadata | None = None
    capabilities: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.version.strip():
            raise ValueError("MCP server requires name and version")
        if any(not capability.strip() for capability in self.capabilities):
            raise ValueError("MCP capabilities must be non-empty")
        _validate_metadata(self.metadata)

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "version": self.version,
            "transport": self.transport.as_payload(),
            "capabilities": list(self.capabilities),
        }
        if self.auth is not None:
            payload["auth"] = self.auth.as_payload()
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


@dataclass(frozen=True, slots=True)
class MCPToolRef:
    server_name: str
    tool_name: str
    version: str | None = None
    required_scopes: tuple[str, ...] = ()
    approval_required: bool = True
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.server_name.strip() or not self.tool_name.strip():
            raise ValueError("MCP tool reference requires server and tool names")
        if self.version is not None and not self.version.strip():
            raise ValueError("MCP tool version must be non-empty when supplied")
        if any(not scope.strip() for scope in self.required_scopes):
            raise ValueError("MCP required scopes must be non-empty")
        _validate_metadata(self.metadata)

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "server_name": self.server_name,
            "tool_name": self.tool_name,
            "required_scopes": list(self.required_scopes),
            "approval_required": self.approval_required,
        }
        if self.version is not None:
            payload["version"] = self.version
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload
