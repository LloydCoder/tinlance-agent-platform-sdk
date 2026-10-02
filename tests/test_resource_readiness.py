from tinlance_agent_platform_sdk.features import PAGINATION, WEBHOOKS


def test_resource_lifecycle_features_are_contract_gated() -> None:
    assert PAGINATION.name == "pagination"
    assert PAGINATION.required_platform_contract == "platform.pagination.v1"
    assert WEBHOOKS.name == "webhooks"
    assert WEBHOOKS.required_platform_contract == "platform.webhooks.v1"
