"""Bounded retry policy for the Tinlance Agent Platform SDK.

Retries are deliberately conservative: only transient HTTP responses are eligible,
and consequential operations require explicit opt-in because a transport failure
can leave the remote outcome unknown even when an idempotency key is present.
"""

from __future__ import annotations

import email.utils
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

TRANSIENT_STATUS_CODES = frozenset({429, 502, 503, 504})


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Immutable, bounded retry configuration."""

    max_attempts: int = 3
    initial_delay: float = 0.25
    max_delay: float = 4.0
    jitter: float = 0.1
    retry_consequential: bool = False

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_delay < 0 or self.max_delay < 0:
            raise ValueError("retry delays must not be negative")
        if self.max_delay < self.initial_delay:
            raise ValueError("max_delay must be >= initial_delay")
        if self.jitter < 0 or self.jitter > 1:
            raise ValueError("jitter must be between 0 and 1")

    def allows(self, *, consequential: bool, status_code: int | None) -> bool:
        if consequential and not self.retry_consequential:
            return False
        return status_code in TRANSIENT_STATUS_CODES

    def delay(self, attempt: int, retry_after: str | None = None) -> float:
        """Return a bounded delay, honoring a valid HTTP Retry-After value."""
        if retry_after:
            parsed = _parse_retry_after(retry_after)
            if parsed is not None:
                return min(parsed, self.max_delay)
        base = min(self.max_delay, self.initial_delay * (2 ** max(0, attempt - 1)))
        if not self.jitter:
            return base
        return min(self.max_delay, base + random.uniform(0.0, base * self.jitter))

    def sleep(self, attempt: int, retry_after: str | None = None) -> None:
        time.sleep(self.delay(attempt, retry_after))


def _parse_retry_after(value: str) -> float | None:
    value = value.strip()
    seconds: float
    try:
        seconds = float(value)
    except ValueError:
        try:
            date = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        if date.tzinfo is None:
            date = date.replace(tzinfo=UTC)
        seconds = float((date - datetime.now(UTC)).total_seconds())
    return max(0.0, seconds)


def retry_call(
    operation: Callable[[], object],
    *,
    policy: RetryPolicy,
    consequential: bool,
    status_getter: Callable[[BaseException], tuple[int | None, str | None]],
) -> object:
    """Execute a callback with bounded retries for retryable exceptions.

    The callback must be deterministic with respect to the request identity.
    """
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except BaseException as exc:
            status, retry_after = status_getter(exc)
            if attempt >= policy.max_attempts or not policy.allows(
                consequential=consequential, status_code=status
            ):
                raise
            policy.sleep(attempt, retry_after)
    raise AssertionError("retry loop exhausted without returning or raising")
