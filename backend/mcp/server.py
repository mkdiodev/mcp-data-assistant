"""
MCP Server Configuration

Initializes the FastMCP server and registers all tools.
"""

from fastmcp import FastMCP
from backend.core.logger import log
from backend.mcp.tools.file_tool import register_file_tools
from backend.mcp.tools.db_tool import register_db_tools


# Create MCP server instance
mcp = FastMCP(
    name="mcp-data-assistant",
)


def setup_tools() -> None:
    """Register all tools with the MCP server."""
    log.info("Registering MCP tools...")

    # Register file tools
    register_file_tools(mcp)
    log.info("File tools registered successfully")

    # Register database tools
    register_db_tools(mcp)
    log.info("Database tools registered successfully")

    log.info("All MCP tools registered")


# Setup tools on module import
setup_tools()