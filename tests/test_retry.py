from tinlance_agent_platform_sdk import RetryPolicy


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
