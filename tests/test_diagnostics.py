from tinlance_agent_platform_sdk.diagnostics import diagnostics


def test_diagnostics_contains_no_credentials() -> None:
    result = diagnostics()
    assert result["sdk_version"] == "1.0.0"
    assert result["platform_api_version"] == "1.1"
    assert "token" not in {key.lower() for key in result}
    assert "authorization" not in {key.lower() for key in result}
