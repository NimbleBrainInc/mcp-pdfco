"""Entry point for running mcp_pdfco as a module."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
