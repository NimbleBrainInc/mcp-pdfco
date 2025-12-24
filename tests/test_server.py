"""Unit tests for the MCP server tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_pdfco.api_models import (
    BarcodeGenerateResponse,
    BarcodeReadResponse,
    HTMLToPDFResponse,
    ImageToPDFResponse,
    PDFCompressResponse,
    PDFInfoDetails,
    PDFInfoResponse,
    PDFMergeResponse,
    PDFProtectResponse,
    PDFSplitResponse,
    PDFToCSVResponse,
    PDFToHTMLResponse,
    PDFToJSONResponse,
    PDFToTextResponse,
    PDFUnlockResponse,
    URLToPDFResponse,
)
from mcp_pdfco.server import mcp


@pytest.fixture
def mcp_server():
    """Provide the MCP server instance."""
    return mcp


def parse_result(result):
    """Parse the JSON text content from a tool result."""
    return json.loads(result.content[0].text)


class TestPDFConversionTools:
    """Test PDF conversion tools."""

    @pytest.mark.asyncio
    async def test_pdf_to_text(self, mcp_server):
        """Test pdf_to_text tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFToTextResponse(error=False, text="Sample text")
            mock_client.pdf_to_text.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_to_text", {"url": "http://example.com/test.pdf"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["text"] == "Sample text"
            mock_client.pdf_to_text.assert_called_once_with(
                "http://example.com/test.pdf", None, False
            )

    @pytest.mark.asyncio
    async def test_pdf_to_json(self, mcp_server):
        """Test pdf_to_json tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFToJSONResponse(error=False, data={"key": "value"})
            mock_client.pdf_to_json.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_to_json", {"url": "http://example.com/test.pdf"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["data"] == {"key": "value"}
            mock_client.pdf_to_json.assert_called_once_with("http://example.com/test.pdf", None)

    @pytest.mark.asyncio
    async def test_pdf_to_html(self, mcp_server):
        """Test pdf_to_html tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFToHTMLResponse(error=False, html="<html>content</html>")
            mock_client.pdf_to_html.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_to_html", {"url": "http://example.com/test.pdf"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["html"] == "<html>content</html>"

    @pytest.mark.asyncio
    async def test_pdf_to_csv(self, mcp_server):
        """Test pdf_to_csv tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFToCSVResponse(error=False, csv="col1,col2\nval1,val2")
            mock_client.pdf_to_csv.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_to_csv", {"url": "http://example.com/test.pdf"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["csv"] == "col1,col2\nval1,val2"


class TestPDFManipulationTools:
    """Test PDF manipulation tools."""

    @pytest.mark.asyncio
    async def test_pdf_merge(self, mcp_server):
        """Test pdf_merge tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFMergeResponse(error=False, url="http://example.com/merged.pdf")
            mock_client.pdf_merge.return_value = mock_response

            urls = ["http://example.com/1.pdf", "http://example.com/2.pdf"]
            async with Client(mcp_server) as client:
                result = await client.call_tool("pdf_merge", {"urls": urls})

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/merged.pdf"
            mock_client.pdf_merge.assert_called_once_with(urls, "merged.pdf", False)

    @pytest.mark.asyncio
    async def test_pdf_split(self, mcp_server):
        """Test pdf_split tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFSplitResponse(error=False, urls=["http://example.com/page1.pdf"])
            mock_client.pdf_split.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool("pdf_split", {"url": "http://example.com/test.pdf"})

            data = parse_result(result)
            assert data["error"] is False
            assert len(data["urls"]) == 1

    @pytest.mark.asyncio
    async def test_pdf_info(self, mcp_server):
        """Test pdf_info tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFInfoResponse(error=False, info=PDFInfoDetails(PageCount=10))
            mock_client.pdf_info.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool("pdf_info", {"url": "http://example.com/test.pdf"})

            data = parse_result(result)
            assert data["error"] is False
            assert data["info"]["PageCount"] == 10

    @pytest.mark.asyncio
    async def test_pdf_compress(self, mcp_server):
        """Test pdf_compress tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFCompressResponse(
                error=False, url="http://example.com/compressed.pdf"
            )
            mock_client.pdf_compress.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_compress", {"url": "http://example.com/test.pdf"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/compressed.pdf"


class TestBarcodeTools:
    """Test barcode tools."""

    @pytest.mark.asyncio
    async def test_barcode_generate(self, mcp_server):
        """Test barcode_generate tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = BarcodeGenerateResponse(
                error=False, url="http://example.com/barcode.png"
            )
            mock_client.barcode_generate.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool("barcode_generate", {"value": "test123"})

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/barcode.png"

    @pytest.mark.asyncio
    async def test_barcode_read(self, mcp_server):
        """Test barcode_read tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = BarcodeReadResponse(error=False, barcodes=[])
            mock_client.barcode_read.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "barcode_read", {"url": "http://example.com/image.png"}
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["barcodes"] == []


class TestConversionTools:
    """Test conversion to PDF tools."""

    @pytest.mark.asyncio
    async def test_html_to_pdf(self, mcp_server):
        """Test html_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = HTMLToPDFResponse(error=False, url="http://example.com/output.pdf")
            mock_client.html_to_pdf.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool("html_to_pdf", {"html": "<html>test</html>"})

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/output.pdf"

    @pytest.mark.asyncio
    async def test_url_to_pdf(self, mcp_server):
        """Test url_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = URLToPDFResponse(error=False, url="http://example.com/webpage.pdf")
            mock_client.url_to_pdf.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool("url_to_pdf", {"url": "http://example.com"})

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/webpage.pdf"

    @pytest.mark.asyncio
    async def test_image_to_pdf(self, mcp_server):
        """Test image_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = ImageToPDFResponse(error=False, url="http://example.com/images.pdf")
            mock_client.image_to_pdf.return_value = mock_response

            images = ["http://example.com/img1.png"]
            async with Client(mcp_server) as client:
                result = await client.call_tool("image_to_pdf", {"images": images})

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/images.pdf"


class TestSecurityTools:
    """Test PDF security tools."""

    @pytest.mark.asyncio
    async def test_pdf_protect(self, mcp_server):
        """Test pdf_protect tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFProtectResponse(error=False, url="http://example.com/protected.pdf")
            mock_client.pdf_protect.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_protect",
                    {"url": "http://example.com/test.pdf", "owner_password": "owner123"},
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/protected.pdf"

    @pytest.mark.asyncio
    async def test_pdf_unlock(self, mcp_server):
        """Test pdf_unlock tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = PDFUnlockResponse(error=False, url="http://example.com/unlocked.pdf")
            mock_client.pdf_unlock.return_value = mock_response

            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "pdf_unlock",
                    {"url": "http://example.com/test.pdf", "password": "password123"},
                )

            data = parse_result(result)
            assert data["error"] is False
            assert data["url"] == "http://example.com/unlocked.pdf"
