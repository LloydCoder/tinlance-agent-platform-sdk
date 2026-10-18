from __future__ import annotations

import pytest

from tinlance_agent_platform_sdk.trace_context import TraceEvidenceRef, TraceLineageContext


def make_context(**overrides) -> TraceLineageContext:
    values = {
        "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
        "span_id": "00f067aa0ba902b7",
        "correlation_id": "corr-1",
        "request_id": "req-1",
        "tenant_id": "tenant-a",
        "operation": "platform.execute",
        "started_at": "2026-10-18T05:00:00Z",
        "safe_attributes": (("service", "platform"), ("outcome", "started"), ("attempt", 0)),
    }
    values.update(overrides)
    return TraceLineageContext(**values)


def test_trace_lineage_serializes_correlation_and_digest_addressed_evidence() -> None:
    evidence = TraceEvidenceRef(
        evidence_id="evidence:policy-decision:1",
        kind="policy-decision",
        sha256="a" * 64,
        source="platform.policy",
        observed_at="2026-10-18T05:00:01Z",
    )
    payload = make_context(evidence_refs=(evidence,)).as_payload()
    assert payload["schema_version"] == "trace-context/v1"
    assert payload["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert payload["tenant_id"] == "tenant-a"
    assert child.as_headers()["traceparent"] == "00-4bf92f3577b34da6a3ce929d0e0e4736-1111111111111111-00"
    assert payload["evidence_refs"][0]["sha256"] == "a" * 64
    assert "authorization" not in payload


def test_child_span_preserves_trace_and_correlation_scope() -> None:
    child = make_context().child(
        span_id="1111111111111111",
        operation="platform.policy.evaluate",
        started_at="2026-10-18T05:00:02Z",
    )
    payload = child.as_payload()
    assert payload["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert payload["parent_span_id"] == "00f067aa0ba902b7"
    assert payload["correlation_id"] == "corr-1"
    assert payload["tenant_id"] == "tenant-a"


@pytest.mark.parametrize(
    "overrides",
    [
        {"trace_id": "0" * 32},
        {"span_id": "0" * 16},
        {"parent_span_id": "not-a-span"},
        {"started_at": "2026-10-18T05:00:00"},
        {"data_classification": "top-secret"},
        {"safe_attributes": (("authorization", "Bearer abc"),)},
        {"safe_attributes": (("prompt", "private prompt"),)},
    ],
)
def test_invalid_or_sensitive_trace_context_is_rejected(overrides) -> None:
    with pytest.raises(ValueError):
        make_context(**overrides)


def test_evidence_reference_requires_sha256_digest() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        TraceEvidenceRef(evidence_id="evidence:1", kind="tool-output", sha256="not-a-digest")
