"""Canonical CloudEvents 1.0 JSON envelope used across Tinlance services.

Events are untrusted observations, not authority grants. The Platform remains
the sole authority for identity, policy, approvals and consequential execution.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any

_TRACE_ID = re.compile(r"^[0-9a-f]{32}$")
_SPAN_ID = re.compile(r"^[0-9a-f]{16}$")
_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}


def _required(value: str, name: str, limit: int = 256) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{name} must be a normalized non-empty string")
    if len(value) > limit:
        raise ValueError(f"{name} exceeds {limit} characters")


def _timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("time must be an RFC 3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("time must include a timezone")


@dataclass(frozen=True, slots=True)
class CloudEvent:
    id: str
    source: str
    type: str
    time: str
    tenantid: str
    executionid: str
    traceid: str
    correlationid: str
    data: Mapping[str, Any]
    subject: str | None = None
    spanid: str | None = None
    causationid: str | None = None
    workspaceid: str | None = None
    organizationid: str | None = None
    actorid: str | None = None
    agentid: str | None = None
    dataclassification: str | None = None
    dataschema: str | None = None
    specversion: str = "1.0"
    datacontenttype: str = "application/json"

    def __post_init__(self) -> None:
        if self.specversion != "1.0":
            raise ValueError("only CloudEvents specversion 1.0 is supported")
        if self.datacontenttype != "application/json":
            raise ValueError("datacontenttype must be application/json")
        for value, name, limit in (
            (self.id, "id", 256),
            (self.source, "source", 2048),
            (self.type, "type", 256),
            (self.tenantid, "tenantid", 256),
            (self.executionid, "executionid", 256),
            (self.correlationid, "correlationid", 256),
        ):
            _required(value, name, limit)
        _timestamp(self.time)
        if not _TRACE_ID.fullmatch(self.traceid) or set(self.traceid) == {"0"}:
            raise ValueError("traceid must be a valid non-zero W3C trace identifier")
        if self.spanid is not None and (
            not _SPAN_ID.fullmatch(self.spanid) or set(self.spanid) == {"0"}
        ):
            raise ValueError("spanid must be a valid non-zero W3C span identifier")
        for value, name, limit in (
            (self.subject, "subject", 1024),
            (self.causationid, "causationid", 256),
            (self.workspaceid, "workspaceid", 256),
            (self.organizationid, "organizationid", 256),
            (self.actorid, "actorid", 256),
            (self.agentid, "agentid", 256),
            (self.dataschema, "dataschema", 2048),
        ):
            if value is not None:
                _required(value, name, limit)
        if self.dataclassification is not None and self.dataclassification not in _CLASSIFICATIONS:
            raise ValueError("unsupported dataclassification")
        if not isinstance(self.data, Mapping):
            raise ValueError("data must be a JSON object")
        try:
            encoded = json.dumps(
                dict(self.data), sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            # A fresh top-level mapping prevents callers mutating the original mapping.
            object.__setattr__(self, "data", MappingProxyType(json.loads(encoded)))
        except (TypeError, ValueError) as exc:
            raise ValueError("data must contain only finite JSON-compatible values") from exc

    def as_payload(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "specversion": self.specversion,
            "id": self.id,
            "source": self.source,
            "type": self.type,
            "time": self.time,
            "datacontenttype": self.datacontenttype,
            "tenantid": self.tenantid,
            "executionid": self.executionid,
            "traceid": self.traceid,
            "correlationid": self.correlationid,
            "data": dict(self.data),
        }
        for name in (
            "subject",
            "spanid",
            "causationid",
            "workspaceid",
            "organizationid",
            "actorid",
            "agentid",
            "dataclassification",
            "dataschema",
        ):
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        return result

    def to_json(self) -> str:
        return json.dumps(self.as_payload(), sort_keys=True, separators=(",", ":"), allow_nan=False)
