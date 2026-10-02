"""Optional, authority-neutral telemetry hooks for the SDK.

The SDK emits only operation/request metadata and never exports bearer
credentials or request/response payloads through this interface.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class TelemetrySink(Protocol):
    """Minimal callback surface that can be adapted to OpenTelemetry."""

    def on_request(self, *, operation: str, request_id: str) -> None: ...

    def on_response(
        self,
        *,
        operation: str,
        request_id: str,
        status_code: int,
        elapsed_ms: float,
    ) -> None: ...

    def on_error(
        self,
        *,
        operation: str,
        request_id: str,
        error_type: str,
        status_code: int | None,
        elapsed_ms: float,
    ) -> None: ...


def safe_attributes(
    *,
    operation: str,
    request_id: str,
    status_code: int | None = None,
    elapsed_ms: float | None = None,
) -> Mapping[str, str | int | float]:
    """Return an allow-listed telemetry attribute set with no payloads."""
    attributes: dict[str, str | int | float] = {
        "tinlance.operation": operation,
        "tinlance.request_id": request_id,
    }
    if status_code is not None:
        attributes["http.status_code"] = status_code
    if elapsed_ms is not None:
        attributes["tinlance.elapsed_ms"] = elapsed_ms
    return attributes
