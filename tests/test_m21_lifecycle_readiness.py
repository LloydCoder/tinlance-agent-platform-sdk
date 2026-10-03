from tinlance_agent_platform_sdk.compat import DEFERRED_OPERATIONS, PUBLIC_OPERATIONS


def test_run_lifecycle_future_operations_remain_contract_gated() -> None:
    assert {"runs.get", "runs.wait"}.issubset(DEFERRED_OPERATIONS)
    assert not {"runs.get", "runs.wait", "runs.resume"} & PUBLIC_OPERATIONS
