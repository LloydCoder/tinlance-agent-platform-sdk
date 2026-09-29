from __future__ import annotations

import re
from collections.abc import MutableMapping
from dataclasses import dataclass


_TRACEPARENT = re.compile(r"^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$")
_TRACESTATE_MAX = 512


def validate_traceparent(value: str) -> str:
    if not isinstance(value, str) or not _TRACEPARENT.fullmatch(value):
        raise ValueError("traceparent must use W3C Trace Context format")
    version = value[:2]
    trace_id = value[3:35]
    parent_id = value[36:52]
    flags = value[53:55]
    if version == "ff":
        raise ValueError("traceparent version ff is forbidden")
    if trace_id == "0" * 32 or parent_id == "0" * 16:
        raise ValueError("traceparent identifiers must not be all zero")
    if version == "00" and int(flags, 16) & 0xFE:
        raise ValueError("unsupported traceparent flags are set")
    return value


def validate_tracestate(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > _TRACESTATE_MAX:
        raise ValueError("tracestate must be non-empty and at most 512 characters")
    if any(ord(char) < 0x20 or ord(char) > 0x7E for char in value):
        raise ValueError("tracestate must contain visible ASCII characters")
    return value


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Immutable W3C trace context suitable for request propagation."""

    traceparent: str
    tracestate: str | None = None

    def __post_init__(self) -> None:
        validate_traceparent(self.traceparent)
        if self.tracestate is not None:
            validate_tracestate(self.tracestate)

    @classmethod
    def from_headers(cls, headers: MutableMapping[str, str]) -> TraceContext | None:
        traceparent = next((v for k, v in headers.items() if k.lower() == "traceparent"), None)
        if traceparent is None:
            return None
        tracestate = next((v for k, v in headers.items() if k.lower() == "tracestate"), None)
        return cls(traceparent, tracestate)

    def inject(self, headers: MutableMapping[str, str]) -> None:
        headers["traceparent"] = self.traceparent
        if self.tracestate is not None:
            headers["tracestate"] = self.tracestate

    def as_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        self.inject(headers)
        return headers
