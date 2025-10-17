"""Unit tests for the PDF.co API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_pdfco.api_client import PDFcoAPIError, PDFcoClient


@pytest.fixture
async def client():
    """Create a test client."""
    client = PDFcoClient(api_key="test_key")
    await client._ensure_session()
    yield client
    await client.close()


class TestPDFcoClient:
    """Test the PDFco API client."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = PDFcoClient(api_key="test_key", timeout=60.0)
        assert client.api_key == "test_key"
        assert client.timeout == 60.0
        assert client.base_url == "https://api.pdf.co/v1"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client context manager."""
        async with PDFcoClient(api_key="test_key") as client:
            assert client._session is not None

    @pytest.mark.asyncio
    async def test_pdf_to_text_success(self, client):
        """Test successful pdf_to_text call."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {
            "error": False,
            "text": "Sample text",
            "pageCount": 1,
        }

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            result = await client.pdf_to_text("http://example.com/test.pdf")

            assert result.error is False
            assert result.text == "Sample text"
            assert result.pageCount == 1

    @pytest.mark.asyncio
    async def test_pdf_to_json_success(self, client):
        """Test successful pdf_to_json call."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {
            "error": False,
            "data": {"key": "value"},
            "pageCount": 1,
        }

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            result = await client.pdf_to_json("http://example.com/test.pdf")

            assert result.error is False
            assert result.data == {"key": "value"}

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {"error": True, "message": "Bad request"}

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            with pytest.raises(PDFcoAPIError) as exc_info:
                await client.pdf_to_text("http://example.com/test.pdf")

            assert exc_info.value.status == 400
            assert "Bad request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pdf_merge(self, client):
        """Test pdf_merge method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {
            "error": False,
            "url": "http://example.com/merged.pdf",
            "pageCount": 5,
        }

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            urls = ["http://example.com/1.pdf", "http://example.com/2.pdf"]
            result = await client.pdf_merge(urls)

            assert result.error is False
            assert result.url == "http://example.com/merged.pdf"

    @pytest.mark.asyncio
    async def test_barcode_generate(self, client):
        """Test barcode_generate method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {
            "error": False,
            "url": "http://example.com/barcode.png",
        }

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            result = await client.barcode_generate("test123")

            assert result.error is False
            assert result.url == "http://example.com/barcode.png"

    @pytest.mark.asyncio
    async def test_pdf_compress(self, client):
        """Test pdf_compress method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {
            "error": False,
            "url": "http://example.com/compressed.pdf",
            "originalSize": 1000000,
            "compressedSize": 500000,
            "compressionRatio": 50.0,
        }

        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            result = await client.pdf_compress("http://example.com/test.pdf")

            assert result.error is False
            assert result.url == "http://example.com/compressed.pdf"
            assert result.compressionRatio == 50.0
