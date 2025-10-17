"""Unit tests for the MCP server tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import Context

from mcp_pdfco.server import (
    barcode_generate,
    barcode_read,
    html_to_pdf,
    image_to_pdf,
    pdf_compress,
    pdf_info,
    pdf_merge,
    pdf_protect,
    pdf_split,
    pdf_to_csv,
    pdf_to_html,
    pdf_to_json,
    pdf_to_text,
    pdf_unlock,
    url_to_pdf,
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = MagicMock(spec=Context)
    ctx.warning = MagicMock()
    ctx.error = MagicMock()
    return ctx


class TestPDFConversionTools:
    """Test PDF conversion tools."""

    @pytest.mark.asyncio
    async def test_pdf_to_text(self, mock_context):
        """Test pdf_to_text tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.text = "Sample text"
            mock_client.pdf_to_text.return_value = mock_response

            result = await pdf_to_text("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.text == "Sample text"
            mock_client.pdf_to_text.assert_called_once_with(
                "http://example.com/test.pdf", None, False
            )

    @pytest.mark.asyncio
    async def test_pdf_to_json(self, mock_context):
        """Test pdf_to_json tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.data = {"key": "value"}
            mock_client.pdf_to_json.return_value = mock_response

            result = await pdf_to_json("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.data == {"key": "value"}
            mock_client.pdf_to_json.assert_called_once_with("http://example.com/test.pdf", None)

    @pytest.mark.asyncio
    async def test_pdf_to_html(self, mock_context):
        """Test pdf_to_html tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.html = "<html>content</html>"
            mock_client.pdf_to_html.return_value = mock_response

            result = await pdf_to_html("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.html == "<html>content</html>"

    @pytest.mark.asyncio
    async def test_pdf_to_csv(self, mock_context):
        """Test pdf_to_csv tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.csv = "col1,col2\nval1,val2"
            mock_client.pdf_to_csv.return_value = mock_response

            result = await pdf_to_csv("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.csv == "col1,col2\nval1,val2"


class TestPDFManipulationTools:
    """Test PDF manipulation tools."""

    @pytest.mark.asyncio
    async def test_pdf_merge(self, mock_context):
        """Test pdf_merge tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/merged.pdf"
            mock_client.pdf_merge.return_value = mock_response

            urls = ["http://example.com/1.pdf", "http://example.com/2.pdf"]
            result = await pdf_merge(urls, ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/merged.pdf"
            mock_client.pdf_merge.assert_called_once_with(urls, "merged.pdf", False)

    @pytest.mark.asyncio
    async def test_pdf_split(self, mock_context):
        """Test pdf_split tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.urls = ["http://example.com/page1.pdf"]
            mock_client.pdf_split.return_value = mock_response

            result = await pdf_split("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert len(result.urls) == 1

    @pytest.mark.asyncio
    async def test_pdf_info(self, mock_context):
        """Test pdf_info tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.pageCount = 10
            mock_client.pdf_info.return_value = mock_response

            result = await pdf_info("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.pageCount == 10

    @pytest.mark.asyncio
    async def test_pdf_compress(self, mock_context):
        """Test pdf_compress tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/compressed.pdf"
            mock_client.pdf_compress.return_value = mock_response

            result = await pdf_compress("http://example.com/test.pdf", ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/compressed.pdf"


class TestBarcodeTools:
    """Test barcode tools."""

    @pytest.mark.asyncio
    async def test_barcode_generate(self, mock_context):
        """Test barcode_generate tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/barcode.png"
            mock_client.barcode_generate.return_value = mock_response

            result = await barcode_generate("test123", ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/barcode.png"

    @pytest.mark.asyncio
    async def test_barcode_read(self, mock_context):
        """Test barcode_read tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.barcodes = []
            mock_client.barcode_read.return_value = mock_response

            result = await barcode_read("http://example.com/image.png", ctx=mock_context)

            assert result.error is False
            assert result.barcodes == []


class TestConversionTools:
    """Test conversion to PDF tools."""

    @pytest.mark.asyncio
    async def test_html_to_pdf(self, mock_context):
        """Test html_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/output.pdf"
            mock_client.html_to_pdf.return_value = mock_response

            result = await html_to_pdf("<html>test</html>", ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/output.pdf"

    @pytest.mark.asyncio
    async def test_url_to_pdf(self, mock_context):
        """Test url_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/webpage.pdf"
            mock_client.url_to_pdf.return_value = mock_response

            result = await url_to_pdf("http://example.com", ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/webpage.pdf"

    @pytest.mark.asyncio
    async def test_image_to_pdf(self, mock_context):
        """Test image_to_pdf tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/images.pdf"
            mock_client.image_to_pdf.return_value = mock_response

            images = ["http://example.com/img1.png"]
            result = await image_to_pdf(images, ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/images.pdf"


class TestSecurityTools:
    """Test PDF security tools."""

    @pytest.mark.asyncio
    async def test_pdf_protect(self, mock_context):
        """Test pdf_protect tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/protected.pdf"
            mock_client.pdf_protect.return_value = mock_response

            result = await pdf_protect("http://example.com/test.pdf", "owner123", ctx=mock_context)

            assert result.error is False
            assert result.url == "http://example.com/protected.pdf"

    @pytest.mark.asyncio
    async def test_pdf_unlock(self, mock_context):
        """Test pdf_unlock tool."""
        with patch("mcp_pdfco.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_response = MagicMock()
            mock_response.error = False
            mock_response.url = "http://example.com/unlocked.pdf"
            mock_client.pdf_unlock.return_value = mock_response

            result = await pdf_unlock(
                "http://example.com/test.pdf", "password123", ctx=mock_context
            )

            assert result.error is False
            assert result.url == "http://example.com/unlocked.pdf"
