"""
MCP Resources (read-only data access).
"""

import json

from .config import PROGRESS_DIR
from .storage import load_json


def register_resources(mcp):
    """Register MCP resources with the server."""

    @mcp.resource("profile://current")
    def get_profile_resource() -> str:
        """Current user reading profile."""
        profile = load_json("profile")
        if not profile:
            return json.dumps({"message": "No profile yet. Run start_interview to create one."})
        return json.dumps(profile, indent=2)

    @mcp.resource("bookstacks://all")
    def get_all_stacks_resource() -> str:
        """All reading stacks across domains."""
        stacks = load_json("bookstacks")
        if not stacks.get("stacks"):
            return json.dumps({"message": "No bookstacks yet. Use build_bookstack to create some."})
        return json.dumps(stacks, indent=2)

    @mcp.resource("log://recent")
    def get_recent_log_resource() -> str:
        """Recent reading log entries (last 10)."""
        log = load_json("reading_log", PROGRESS_DIR)
        entries = log.get("entries", [])[-10:]
        if not entries:
            return json.dumps({"message": "No books logged yet."})
        return json.dumps(entries, indent=2)
