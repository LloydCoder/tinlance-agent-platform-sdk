from tinlance_agent_platform_sdk.compat import (
    DEFERRED_OPERATIONS,
    EXPECTED_SUCCESS_STATUS,
    PUBLIC_OPERATIONS,
    PLATFORM_API_VERSION,
    assert_contract_integrity,
    supports_platform_api,
)


def test_contract_manifest_is_disjoint_and_complete() -> None:
    assert_contract_integrity()
    assert PUBLIC_OPERATIONS.isdisjoint(DEFERRED_OPERATIONS)
    assert PUBLIC_OPERATIONS == frozenset(EXPECTED_SUCCESS_STATUS)


def test_supported_platform_version_is_explicit() -> None:
    assert supports_platform_api(PLATFORM_API_VERSION)
    assert not supports_platform_api("999.0")
