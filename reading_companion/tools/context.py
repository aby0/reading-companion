"""
Stage 2: Context Builder Tools

Tools for extracting and updating latent features from the user profile.
"""

from datetime import datetime

from ..storage import load_json, save_json, load_prompt
from ..markdown import save_profile_markdown


def register_context_tools(mcp):
    """Register context builder tools with the MCP server."""

    @mcp.tool()
    def extract_context() -> dict:
        """
        Analyze the profile to extract latent features.

        Returns the context builder prompt along with the current profile.
        After analysis, call update_latent_features with the results.
        """
        profile = load_json("profile")
        if not profile:
            return {"error": "No profile found. Run start_interview first."}

        prompt = load_prompt("context_builder")

        return {
            "instruction": "Analyze this profile and identify latent features",
            "prompt": prompt,
            "profile": profile
        }

    @mcp.tool()
    def update_latent_features(features: dict) -> dict:
        """
        Update the profile with extracted latent features.

        Args:
            features: Dictionary of latent features extracted from analysis.
        """
        profile = load_json("profile")
        if not profile:
            return {"error": "No profile found. Run start_interview first."}

        profile["latent_features"] = features
        profile["updated_at"] = datetime.now().isoformat()

        save_json("profile", profile)
        save_profile_markdown(profile)

        return {
            "status": "updated",
            "message": "Latent features saved to profile",
            "features": features
        }
