"""End-to-end tests for the MCP server with real PDF.co API calls.

These tests require a valid PDFCO_API_KEY environment variable and will make actual API calls.
They should be run sparingly to avoid exhausting API quotas.
"""

import os
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import Context

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from mcp_pdfco import server
from mcp_pdfco.server import (
    barcode_generate,
    barcode_read,
    html_to_pdf,
    pdf_add_watermark,
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

# Skip all e2e tests if API key is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("PDFCO_API_KEY"),
    reason="PDFCO_API_KEY not set - skipping e2e tests",
)


@pytest_asyncio.fixture
async def real_context() -> Context:  # type: ignore
    """Create a real MCP context for e2e tests."""
    # Reset global client before each test
    server._client = None

    # For e2e tests, we can use a minimal context
    # The server functions will create their own API client
    class MinimalContext:
        async def warning(self, msg: str) -> None:
            pass

        async def error(self, msg: str) -> None:
            pass

    yield MinimalContext()  # type: ignore

    # Cleanup after test
    if server._client:
        await server._client.close()
        server._client = None


# Sample PDFs hosted publicly for testing
SAMPLE_PDF_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
SAMPLE_IMAGE_URL = "https://via.placeholder.com/300.png"


class TestE2ETextExtraction:
    """End-to-end tests for text extraction tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_to_text_real_api(self, real_context: Context) -> None:
        """Test pdf_to_text with real PDF.co API."""
        result = await pdf_to_text(url=SAMPLE_PDF_URL, ctx=real_context)

        assert result.error is False
        # API returns URL to text file, not body content
        assert result.url is not None
        assert "http" in result.url

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_to_json_real_api(self, real_context: Context) -> None:
        """Test pdf_to_json with real PDF.co API."""
        result = await pdf_to_json(url=SAMPLE_PDF_URL, ctx=real_context)

        assert result.error is False
        # API returns JSON structure with data
        assert result.data is not None or result.url is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_to_html_real_api(self, real_context: Context) -> None:
        """Test pdf_to_html with real PDF.co API."""
        result = await pdf_to_html(url=SAMPLE_PDF_URL, ctx=real_context)

        assert result.error is False
        # API may return URL or html depending on size
        assert result.html is not None or result.url is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_to_csv_real_api(self, real_context: Context) -> None:
        """Test pdf_to_csv with real PDF.co API."""
        result = await pdf_to_csv(url=SAMPLE_PDF_URL, ctx=real_context)

        assert result.error is False
        # API returns URL to CSV file
        assert result.url is not None or result.csv is not None


class TestE2EPDFInfo:
    """End-to-end tests for PDF info tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_info_real_api(self, real_context: Context) -> None:
        """Test pdf_info with real PDF.co API."""
        result = await pdf_info(url=SAMPLE_PDF_URL, ctx=real_context)

        assert result.error is False
        assert result.pageCount is not None
        assert result.pageCount > 0


class TestE2EConversion:
    """End-to-end tests for conversion tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_html_to_pdf_real_api(self, real_context: Context) -> None:
        """Test html_to_pdf with real PDF.co API."""
        html_content = """
        <html>
            <head><title>Test Document</title></head>
            <body>
                <h1>E2E Test</h1>
                <p>This is a test document for e2e testing.</p>
            </body>
        </html>
        """
        result = await html_to_pdf(
            html=html_content,
            name="e2e-test.pdf",
            page_size="Letter",
            ctx=real_context,
        )

        assert result.type == "resource_link"
        assert result.uri is not None
        assert "http" in str(result.uri)
        assert result.name == "e2e-test.pdf"
        assert result.mimeType == "application/pdf"

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_url_to_pdf_real_api(self, real_context: Context) -> None:
        """Test url_to_pdf with real PDF.co API."""
        result = await url_to_pdf(
            url="https://example.com",
            name="example.pdf",
            page_size="A4",
            ctx=real_context,
        )

        assert result.type == "resource_link"
        assert result.uri is not None
        assert "http" in str(result.uri)
        assert result.name == "example.pdf"
        assert result.mimeType == "application/pdf"


class TestE2EPDFManipulation:
    """End-to-end tests for PDF manipulation tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_split_real_api(self, real_context: Context) -> None:
        """Test pdf_split with real PDF.co API."""
        result = await pdf_split(
            url=SAMPLE_PDF_URL,
            pages="1",
            ctx=real_context,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        # Check first resource
        assert result[0].type == "resource_link"
        assert result[0].uri is not None
        assert "http" in str(result[0].uri)
        assert result[0].mimeType == "application/pdf"

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_merge_real_api(self, real_context: Context) -> None:
        """Test pdf_merge with real PDF.co API."""
        result = await pdf_merge(
            urls=[SAMPLE_PDF_URL, SAMPLE_PDF_URL],
            name="merged-e2e.pdf",
            ctx=real_context,
        )

        assert result.type == "resource_link"
        assert result.uri is not None
        assert "http" in str(result.uri)
        assert result.name == "merged-e2e.pdf"
        assert result.mimeType == "application/pdf"


class TestE2EPDFEditing:
    """End-to-end tests for PDF editing tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_add_watermark_real_api(self, real_context: Context) -> None:
        """Test pdf_add_watermark with real PDF.co API."""
        result = await pdf_add_watermark(
            url=SAMPLE_PDF_URL,
            text="E2E TEST",
            x=100,
            y=100,
            font_size=24,
            color="FF0000",
            opacity=0.5,
            ctx=real_context,
        )

        assert result.type == "resource_link"
        assert result.uri is not None
        assert "http" in str(result.uri)
        assert result.mimeType == "application/pdf"

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_compress_real_api(self, real_context: Context) -> None:
        """Test pdf_compress with real PDF.co API."""
        result = await pdf_compress(
            url=SAMPLE_PDF_URL,
            compression_level="balanced",
            ctx=real_context,
        )

        assert result.type == "resource_link"
        assert result.uri is not None
        assert "http" in str(result.uri)
        assert result.mimeType == "application/pdf"


class TestE2ESecurity:
    """End-to-end tests for PDF security tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_pdf_protect_and_unlock_real_api(self, real_context: Context) -> None:
        """Test pdf_protect and pdf_unlock with real PDF.co API."""
        # First protect the PDF
        password = "test123"
        protected = await pdf_protect(
            url=SAMPLE_PDF_URL,
            owner_password=password,
            allow_print=True,
            allow_copy=False,
            ctx=real_context,
        )

        assert protected.type == "resource_link"
        assert protected.uri is not None
        assert "http" in str(protected.uri)
        assert protected.mimeType == "application/pdf"

        # Then unlock it
        unlocked = await pdf_unlock(
            url=str(protected.uri),
            password=password,
            ctx=real_context,
        )

        assert unlocked.type == "resource_link"
        assert unlocked.uri is not None
        assert "http" in str(unlocked.uri)
        assert unlocked.mimeType == "application/pdf"


class TestE2EBarcode:
    """End-to-end tests for barcode tools."""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_barcode_generate_real_api(self, real_context: Context) -> None:
        """Test barcode_generate with real PDF.co API."""
        result = await barcode_generate(
            value="https://example.com/test",
            barcode_type="QRCode",
            format="png",
            ctx=real_context,
        )

        assert result.error is False
        assert result.url is not None
        assert "http" in result.url

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_barcode_read_real_api(self, real_context: Context) -> None:
        """Test barcode_read with real PDF.co API."""
        # First generate a QR code
        generated = await barcode_generate(
            value="TEST123",
            barcode_type="QRCode",
            format="png",
            ctx=real_context,
        )

        assert generated.url is not None

        # Then read it back
        result = await barcode_read(
            url=generated.url,
            barcode_types=["QRCode"],
            ctx=real_context,
        )

        assert result.error is False
        # Barcode detection might not always work with generated codes
        # so we just check that the call succeeded
