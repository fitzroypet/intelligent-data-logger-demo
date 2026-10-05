"""Optional Anthropic workspace routing; never expose credentials to callers."""
import os


def workspace_headers():
    workspace = os.getenv("ANTHROPIC_WORKSPACE_ID", "").strip()
    return {"anthropic-workspace-id": workspace} if workspace else {}
