"""Explicit idempotency helpers.

These helpers generate replay keys; they do not provide exactly-once semantics.
Only the Platform can enforce idempotency at the authority boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    value: str

    def __post_init__(self) -> None:
        if not self.value or self.value != self.value.strip() or len(self.value) > 256:
            raise ValueError("idempotency key must be normalized and at most 256 characters")
        if any(ord(char) < 0x21 or ord(char) > 0x7E for char in self.value):
            raise ValueError("idempotency key must contain printable ASCII only")

    @classmethod
    def for_intent(cls, operation: str, payload: dict[str, object]) -> IdempotencyKey:
        if not operation.strip():
            raise ValueError("operation is required")
        encoded = json.dumps(
            {"operation": operation, "payload": payload},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return cls("tl-" + sha256(encoded).hexdigest())

    def __str__(self) -> str:
        return self.value
