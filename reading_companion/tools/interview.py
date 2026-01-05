"""
Stage 1: Interviewer Tools

Tools for conducting the reading goal interview and saving the user profile.
"""

from datetime import datetime

from ..config import DATA_DIR
from ..storage import load_json, save_json, load_prompt
from ..markdown import save_profile_markdown


def register_interview_tools(mcp):
    """Register interview-related tools with the MCP server."""

    @mcp.tool()
    def start_interview() -> str:
        """
        Begin the reading goal interview.

        Returns the interview prompt to guide the conversation.
        Use this when the user says "interview me" or "set up my profile".
        """
        return load_prompt("interviewer")

    @mcp.tool()
    def save_profile(
        name: str,
        domains: list[dict],
        preferences: dict,
        context: dict
    ) -> dict:
        """
        Save the user's reading profile after the interview.

        Args:
            name: User's name

            domains: List of reading domains with goals. Each domain should have:
                - id: Short identifier (e.g., "classic_lit", "neuroscience")
                - name: Display name (e.g., "Classic Literature")
                - purpose: Why they want to read in this area
                - target_books: Number of books they aim to read

            preferences: Reading preferences dictionary:
                - pacing: "slow_deep" | "steady" | "fast_volume"
                - challenge_tolerance: "low" | "medium" | "high"
                - parallel_books: Number of books they read at once

            context: Current context dictionary:
                - mood: Current reading mood
                - avoidances: List of things to avoid

        Returns:
            Confirmation with status and message
        """
        profile = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "identity": {"name": name},
            "goals": {"domains": domains},
            "preferences": preferences,
            "context": context,
            "latent_features": {}
        }

        save_json("profile", profile)
        save_profile_markdown(profile)

        domain_names = [d.get("name", d.get("id")) for d in domains]

        return {
            "status": "saved",
            "message": f"Profile created for {name}",
            "domains": domain_names,
            "files_created": [
                str(DATA_DIR / "profile.json"),
                str(DATA_DIR / "profile.md")
            ],
            "next_step": "Run extract_context to analyze deeper patterns, then build_bookstack for recommendations"
        }

    @mcp.tool()
    def get_profile() -> dict:
        """Retrieve the current user profile."""
        profile = load_json("profile")
        if not profile:
            return {"error": "No profile found. Run start_interview first."}
        return profile
