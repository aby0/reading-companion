"""
Reading Companion MCP Server

A 4-stage reading companion that integrates with Claude Desktop.
"""

__version__ = "0.1.0"

from mcp.server.fastmcp import FastMCP

from .tools import register_all_tools
from .resources import register_resources

# Initialize MCP server
mcp = FastMCP("Reading Companion")

# Register all tools and resources
register_all_tools(mcp)
register_resources(mcp)


def main():
    """Run the MCP server."""
    mcp.run()
