import pytest

from tinlance_agent_platform_sdk import RetryPolicy
from tinlance_agent_platform_sdk.retry import retry_call


def test_retry_policy_is_bounded_and_conservative() -> None:
    policy = RetryPolicy(max_attempts=3, initial_delay=0, max_delay=1, jitter=0)
    assert policy.allows(consequential=False, status_code=503)
    assert not policy.allows(consequential=True, status_code=503)
    assert not policy.allows(consequential=False, status_code=400)
    assert policy.delay(1) == 0


def test_retry_after_is_bounded() -> None:
    policy = RetryPolicy(max_attempts=2, initial_delay=0, max_delay=2, jitter=0)
    assert policy.delay(1, "120") == 2
    assert policy.delay(1, "invalid") == 0


def test_retry_policy_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(initial_delay=-1)
    with pytest.raises(ValueError):
        RetryPolicy(max_delay=-1)
    with pytest.raises(ValueError):
        RetryPolicy(initial_delay=2, max_delay=1)
    with pytest.raises(ValueError):
        RetryPolicy(jitter=1.1)


def test_retry_after_http_date_is_non_negative() -> None:
    policy = RetryPolicy(initial_delay=0, max_delay=2, jitter=0)
    assert 0 <= policy.delay(1, "Wed, 21 Oct 2015 07:28:00 GMT") <= 2


def test_retry_call_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0
    sleeps: list[float] = []

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("transient")
        return "ok"

    def status_getter(_: BaseException) -> tuple[int | None, str | None]:
        return 503, None

    policy = RetryPolicy(max_attempts=3, initial_delay=0, max_delay=1, jitter=0)
    monkeypatch.setattr(
        "tinlance_agent_platform_sdk.retry.time.sleep",
        lambda _: sleeps.append(0.0),
    )
    assert retry_call(
        operation,
        policy=policy,
        consequential=False,
        status_getter=status_getter,
    ) == "ok"
    assert attempts == 3
    assert len(sleeps) == 2


def test_retry_call_stops_on_non_retryable_error() -> None:
    def operation() -> None:
        raise RuntimeError("bad")

    def status_getter(_: BaseException) -> tuple[int | None, str | None]:
        return 400, None

    with pytest.raises(RuntimeError):
        retry_call(
            operation,
            policy=RetryPolicy(max_attempts=3, initial_delay=0, jitter=0),
            consequential=False,
            status_getter=status_getter,
        )
