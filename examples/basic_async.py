import asyncio

from tinlance_agent_platform_sdk import AsyncAgentPlatform, ClientConfig


async def main() -> None:
    client = AsyncAgentPlatform(
        ClientConfig(
            base_url="https://platform.example",
            bearer_token="opaque-credential",
            tenant_id="tenant-a",
            subject_id="user-a",
        )
    )
    health = await client.health()
    print(health.ready)
    await client.close()


asyncio.run(main())
