"""
MCP Tools organized by stage.
"""

from .interview import register_interview_tools
from .context import register_context_tools
from .syllabus import register_syllabus_tools
from .reflection import register_reflection_tools
from .patterns import register_pattern_tools


def register_all_tools(mcp):
    """Register all tools with the MCP server."""
    register_interview_tools(mcp)
    register_context_tools(mcp)
    register_syllabus_tools(mcp)
    register_reflection_tools(mcp)
    register_pattern_tools(mcp)
