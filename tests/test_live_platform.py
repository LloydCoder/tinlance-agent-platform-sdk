from __future__ import annotations

import os

import pytest

from tinlance_agent_platform_sdk import AgentPlatform

BASE_URL = os.getenv("TINLANCE_PLATFORM_TEST_URL")
TOKEN = os.getenv("TINLANCE_PLATFORM_TEST_TOKEN")
TENANT = os.getenv("TINLANCE_PLATFORM_TEST_TENANT")
SUBJECT = os.getenv("TINLANCE_PLATFORM_TEST_SUBJECT")


@pytest.mark.skipif(
    not all((BASE_URL, TOKEN, TENANT, SUBJECT)),
    reason="live Platform contract test requires TINLANCE_PLATFORM_TEST_* environment variables",
)
def test_live_v1_1_health() -> None:
    assert BASE_URL is not None
    assert TOKEN is not None
    assert TENANT is not None
    assert SUBJECT is not None
    client = AgentPlatform(
        base_url=BASE_URL,
        bearer_token=TOKEN,
        tenant_id=TENANT,
        subject_id=SUBJECT,
    )
    assert client.health().ready is True
