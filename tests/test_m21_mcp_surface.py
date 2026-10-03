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
