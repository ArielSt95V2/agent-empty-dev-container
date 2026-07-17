from tracing import get_client
from langsmith import traceable


@traceable(name="main_agent_workflow")
def agent_workflow():
    """Main agent workflow that will be traced to LangSmith."""
    print("🤖 Agent workflow started")
    
    result = "Agent completed successfully"
    print(f"✓ Result: {result}")
    return result


def main():
    print("Hello from agents!")
    
    client = get_client()
    if client:
        print("📊 Running with LangSmith tracing enabled")
        agent_workflow()
    else:
        print("⚠️  Running without tracing")


if __name__ == "__main__":
    main()