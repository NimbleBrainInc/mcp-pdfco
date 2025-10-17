"""PDF.co MCP Server with comprehensive PDF manipulation tools."""

from .api_client import PDFcoAPIError, PDFcoClient
from .server import app, mcp

__version__ = "1.0.0"

__all__ = ["PDFcoClient", "PDFcoAPIError", "mcp", "app"]
