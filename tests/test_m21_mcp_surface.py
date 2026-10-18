import pytest

from tinlance_agent_platform_sdk import (
    MCPAuthMetadata,
    MCPServerSpec,
    MCPToolRef,
    MCPTransportSpec,
)


def test_mcp_surface_is_metadata_only() -> None:
    server = MCPServerSpec(
        "research-mcp",
        "1.0.0",
        MCPTransportSpec("streamable_http", "https://mcp.example.test/mcp"),
        MCPAuthMetadata(
            "oauth2",
            issuer="https://issuer.example.test",
            audience="mcp",
            scopes=("tools.read",),
        ),
        capabilities=("tools", "resources"),
    )
    tool = MCPToolRef(
        "research-mcp",
        "repository.read",
        "2",
        required_scopes=("tools.read",),
    )
    assert server.as_payload()["transport"]["kind"] == "streamable_http"
    assert tool.as_payload()["approval_required"] is True
    rendered = repr(server.as_payload())
    assert "bearer_token" not in rendered
    assert "client_secret" not in rendered


def test_mcp_transport_validation_is_fail_closed() -> None:
    with pytest.raises(ValueError):
        MCPTransportSpec("streamable_http", "not-an-url")
    with pytest.raises(ValueError):
        MCPTransportSpec("stdio", "https://unexpected.example")
    with pytest.raises(ValueError):
        MCPAuthMetadata("")


def test_mcp_transport_rejects_unsafe_endpoints_and_unknown_versions() -> None:
    for endpoint in (
        "https://user:password@remote.example.test/mcp",
        "http://remote.example.test/mcp",
        "https://127.0.0.1/mcp",
        "https://10.0.0.8/mcp",
        "https://remote.example.test:99999/mcp",
        "https://remote.example.test/mcp?token=unsafe",
        "https://remote.example.test/mcp#fragment",
    ):
        with pytest.raises(ValueError):
            MCPTransportSpec("streamable_http", endpoint)
    with pytest.raises(ValueError):
        MCPTransportSpec("streamable_http", "https://remote.example.test/mcp", ("future-version",))
    with pytest.raises(ValueError):
        MCPTransportSpec("unsupported", "https://remote.example.test/mcp")


def test_mcp_transport_allows_only_loopback_cleartext_development() -> None:
    assert MCPTransportSpec("streamable_http", "http://127.0.0.1:9000/mcp")
    assert MCPTransportSpec("streamable_http", "http://localhost:9000/mcp")
    with pytest.raises(ValueError):
        MCPTransportSpec("streamable_http", "http://192.168.1.10:9000/mcp")


def test_mcp_metadata_rejects_credentials_and_duplicate_keys() -> None:
    with pytest.raises(ValueError, match="credential-shaped"):
        MCPServerSpec(
            "research-mcp",
            "1.0.0",
            MCPTransportSpec("streamable_http", "https://mcp.example.test/mcp"),
            metadata=(("access_token", "not-a-real-token"),),
        )
    with pytest.raises(ValueError, match="credential-shaped"):
        MCPServerSpec(
            "research-mcp",
            "1.0.0",
            MCPTransportSpec("streamable_http", "https://mcp.example.test/mcp"),
            metadata=(("purpose", "Bearer example-token"),),
        )
    with pytest.raises(ValueError, match="credential-shaped"):
        MCPServerSpec(
            "research-mcp",
            "1.0.0",
            MCPTransportSpec("streamable_http", "https://mcp.example.test/mcp"),
            metadata=(("apiKey", "not-a-real-key"),),
        )
    with pytest.raises(ValueError, match="unique"):
        MCPServerSpec(
            "research-mcp",
            "1.0.0",
            MCPTransportSpec("streamable_http", "https://mcp.example.test/mcp"),
            metadata=(("purpose", "research"), ("PURPOSE", "automation")),
        )
