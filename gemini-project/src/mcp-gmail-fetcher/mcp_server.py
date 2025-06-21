"""
Model Context Protocol (MCP) Gmail Fetcher Server implementation.

This module sets up an MCP-compliant server and registers Gmail Fetcher tools
that follow Anthropic's Model Context Protocol specification. These tools can be
accessed by Claude and other MCP-compatible AI models.
"""
from mcp.server.fastmcp import FastMCP
import argparse
import tool_gmail_api
from mylogging import logger
import tool_gemini_api
DEFAULT_PORT = 3001
DEFAULT_CONNECTION_TYPE = "stdio"  # Alternative: "stdio"
def create_mcp_server(port=DEFAULT_PORT):
    """
    Create and configure the Model Context Protocol server.

    Args:
        port: Port number to run the server on

    Returns:
        Configured MCP server instance
    """
    mcp = FastMCP("GmailFetcherService", port=port)

    # Register MCP-compliant tools
    register_tools(mcp)

    return mcp


def register_tools(mcp):
    """
    Register all tools with the MCP server following the Model Context Protocol specification.

    Each tool is decorated with @mcp.tool() to make it available via the MCP interface.

    Args:
        mcp: The MCP server instance
    """

    @mcp.tool()
    async def fetch_gmail_by_receving_time(starttime: str, endtime: str = None):
        """
        fetch gmail received between startime to endtime

        This MCP tool allows AI models to fetch email in the inbox by specifying
        start time and end time.

        Args:
            starttime: time from which we fetch the emails (e.g., 2025-05-14)
            endtime: time to which we fetch the emails(e.g., 2025-05-14)
        Returns:
            A list of email with receiving time between starttime and endtime
        """
        return await tool_gmail_api.get_email(starttime, endtime)



    @mcp.tool()
    async def instruction_to_gemini_flash(prompt: str):
        """
        Send the instruction to Gemini flash model

        This MCP tool allows AI models to send the prompt to Gemini flash model

        Args:
            prompt: the instruction that need to be send to Gemini flash model(e.g., please summarize this text)
        Returns:
            after processing by gemini, return the response from Gemini
        """
        return await tool_gemini_api.get_response_from_flash_model(prompt)

    @mcp.tool()
    async def instruction_to_gemini_text_to_voice(prompt: str, startdate  = str, enddate = str):
        """
        Send the instruction to Gemini text to voice

        This MCP tool allows AI models to send the prompt to Gemini  text to voice model

        Args:
            prompt: the instruction that need to be send to Gemini text to voice model(e.g., this is a text read it)
            starttime: time from which we fetch the emails (e.g., 2025-05-14)
            endtime: time to which we fetch the emails(e.g., 2025-05-14)
        Returns:
            after processing by gemini, return wave file name
        """
        return await tool_gemini_api.get_response_from_text_to_voice_model(prompt, startdate, enddate)



    @mcp.tool()
    def server_status():
        """
        Check if the Model Context Protocol server is running.

        This MCP tool provides a simple way to verify the server is operational.

        Returns:
            A status message indicating the server is online
        """
        return {"status": "online", "message": "MCP gmail fetcher is running"}

    logger.debug("Model Context Protocol tools registered")


def main():
    """
    Main entry point for the Model Context Protocol Gmail Fetcher  Server.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Model Context Protocol Gmail Fetcher  Service")
    parser.add_argument("--connection_type", type=str, default=DEFAULT_CONNECTION_TYPE,
                        choices=["http", "stdio"], help="Connection type (http or stdio)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    args = parser.parse_args()

    # Initialize MCP server
    mcp = create_mcp_server(port=args.port)

    # Determine server type
    server_type = "sse" if args.connection_type == "http" else "stdio"

    # Start the server
    logger.info(
        f"🚀 Starting Model Context Protocol Gmail Fetcher  Service on port {args.port} with {args.connection_type} connection")
    mcp.run(server_type)


if __name__ == "__main__":
    main()