import pytest

from tinlance_agent_platform_sdk import AgentPlatform, ClientConfig


def test_credential_provider_is_used_without_storing_token() -> None:
    client = AgentPlatform(
        base_url="https://platform.example",
        bearer_token="",
        tenant_id="tenant-a",
        subject_id="user-a",
        credential_provider=lambda: "rotated-token",
    )
    assert client._current_credential() == "rotated-token"


def test_invalid_credential_provider_result_fails_closed() -> None:
    client = AgentPlatform(
        base_url="https://platform.example",
        bearer_token="",
        tenant_id="tenant-a",
        subject_id="user-a",
        credential_provider=lambda: "bad token",
    )
    with pytest.raises(ValueError):
        client._current_credential()


def test_client_config_requires_mtls_pair() -> None:
    with pytest.raises(ValueError):
        ClientConfig(
            base_url="https://platform.example",
            tenant_id="tenant-a",
            subject_id="user-a",
            bearer_token="token",
            client_cert="client.pem",
        )


def test_client_config_accepts_rotation_provider() -> None:
    config = ClientConfig(
        base_url="https://platform.example",
        tenant_id="tenant-a",
        subject_id="user-a",
        bearer_token="",
        credential_provider=lambda: "token",
        proxy_url="https://proxy.example:8443",
    )
    assert config.credential_provider is not None
