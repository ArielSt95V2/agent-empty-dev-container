import os
from langsmith import Client


def init_langsmith_tracing():
    """Initialize LangSmith tracing configuration."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    tracing_enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    project_name = os.getenv("LANGSMITH_PROJECT", "agents-dev")
    
    if not api_key:
        raise ValueError("LANGSMITH_API_KEY not set in .env file")
    
    if not tracing_enabled:
        print("⚠️  LangSmith tracing is disabled. Set LANGSMITH_TRACING=true in .env")
        return None
    
    client = Client(api_key=api_key)
    print(f"✅ LangSmith tracing initialized (Project: {project_name})")
    return client


def get_client():
    """Get the LangSmith client instance."""
    return init_langsmith_tracing()