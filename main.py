import asyncio
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    tool,
)
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk

from tracing import get_client

configure_claude_agent_sdk()


@tool(
    "get_weather",
    "Gets the current weather for a given city",
    {"city": str},
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    city = args["city"]
    weather_data = {
        "San Francisco": "Foggy, 62°F",
        "New York": "Sunny, 75°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Clear, 68°F",
    }
    weather = weather_data.get(city, "Weather data not available")
    return {"content": [{"type": "text", "text": f"Weather in {city}: {weather}"}]}

def print_message(message) -> None:
    """Render one agent message as a clean terminal line."""
    if isinstance(message, SystemMessage):
        if message.subtype == "init":
            servers = ", ".join(
                f"{s['name']} ({s['status']})" for s in message.data.get("mcp_servers", [])
            )
            print(f"⚙️  Session started | model: {message.data.get('model')} | MCP: {servers}")
    elif isinstance(message, AssistantMessage):
        if message.error:
            print(f"❌ API error: {message.error}")
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"🤖 Claude: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"🔧 Tool call: {block.name} → {block.input}")
    elif isinstance(message, UserMessage):
        for block in message.content:
            if isinstance(block, ToolResultBlock):
                print(f"   ↳ Tool result: {block.content}")
    elif isinstance(message, ResultMessage):
        status = "❌ FAILED" if message.is_error else "✅ SUCCESS"
        cost = message.total_cost_usd or 0
        print(f"\n{status} | turns: {message.num_turns} | {message.duration_ms} ms | ${cost:.4f}")
        if message.is_error:
            print(f"   Reason: {message.result}")

async def agent_workflow() -> None:
    """Run the quickstart agent. Traced to LangSmith via configure_claude_agent_sdk()."""
    print("🤖 Agent workflow started")

    weather_server = create_sdk_mcp_server(
        name="weather",
        version="1.0.0",
        tools=[get_weather],
    )

    options = ClaudeAgentOptions(
        model="claude-opus-4-8",
        system_prompt="You are a friendly travel assistant who helps with weather information.",
        mcp_servers={"weather": weather_server},
        allowed_tools=["mcp__weather__get_weather"],
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's the weather like in San Francisco and Tokyo?")

        async for message in client.receive_response():
            print_message(message)

    print("✓ Agent workflow finished")


def main():
    print("Hello from agents!")

    client = get_client()
    if client:
        print("📊 Running with LangSmith tracing enabled")
        asyncio.run(agent_workflow())
    else:
        print("⚠️  Running without tracing")


if __name__ == "__main__":
    main()