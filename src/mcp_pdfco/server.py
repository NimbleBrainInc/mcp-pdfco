"""FastMCP server for PDF.co API."""

import json
import logging
import os
import sys
from importlib.resources import files

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import ContentBlock, ResourceLink, TextContent
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api_client import PDFcoAPIError, PDFcoClient
from .api_models import (
    BarcodeGenerateResponse,
    BarcodeReadResponse,
    ImageToPDFResponse,
    OCRPDFResponse,
    PDFCompressResponse,
    PDFInfoResponse,
    PDFProtectResponse,
    PDFRotateResponse,
    PDFSplitResponse,
    PDFToCSVResponse,
    PDFToHTMLResponse,
    PDFToJSONResponse,
    PDFToTextResponse,
    PDFUnlockResponse,
    PDFWatermarkResponse,
    URLToPDFResponse,
)

# Diagnostics go to stderr (stdout carries JSON-RPC), never to the client: MCP's logging
# capability is deprecated as of the 2026-07-28 protocol (SEP-2577). A failure the caller
# must see is raised as a ToolError.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_pdfco")

# Create MCP server
mcp = FastMCP(
    "PDFco",
    instructions=(
        "Before using PDF.co tools, read the skill://pdfco/usage resource "
        "for HTML best practices, tool selection, and error recovery."
    ),
)


SKILL_CONTENT = files("mcp_pdfco").joinpath("SKILL.md").read_text()


@mcp.resource("skill://pdfco/usage")
def pdfco_skill() -> str:
    """How to effectively use PDF.co tools: HTML-to-PDF best practices, tool selection, error recovery."""
    return SKILL_CONTENT


# Global client instance
_client: PDFcoClient | None = None


def get_client() -> PDFcoClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        api_key = os.environ.get("PDFCO_API_KEY")
        if not api_key:
            logger.warning(
                "PDFCO_API_KEY is not set - API calls will fail. "
                "Get your API key from https://app.pdf.co/dashboard"
            )
        _client = PDFcoClient(api_key=api_key)
    return _client


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-pdfco"})


# MCP Tools
@mcp.tool()
async def pdf_to_text(
    url: str,
    pages: str | None = None,
    async_mode: bool = False,
) -> PDFToTextResponse:
    """Extract text from PDF.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3" or "1,3,5")
        async_mode: Process asynchronously (default: false)

    Returns:
        PDFToTextResponse with extracted text content
    """
    client = get_client()
    try:
        return await client.pdf_to_text(url, pages, async_mode)
    except PDFcoAPIError as e:
        logger.warning("PDF to text conversion failed: %s", e.message)
        raise ToolError(f"PDF to text conversion failed: {e.message}") from e


@mcp.tool()
async def pdf_to_json(
    url: str,
    pages: str | None = None,
) -> PDFToJSONResponse:
    """Extract structured data from PDF.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")

    Returns:
        PDFToJSONResponse with structured data
    """
    client = get_client()
    try:
        return await client.pdf_to_json(url, pages)
    except PDFcoAPIError as e:
        logger.warning("PDF to JSON conversion failed: %s", e.message)
        raise ToolError(f"PDF to JSON conversion failed: {e.message}") from e


@mcp.tool()
async def pdf_to_html(
    url: str,
    pages: str | None = None,
    simple: bool = False,
) -> PDFToHTMLResponse:
    """Convert PDF to HTML.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        simple: Use simple HTML mode (default: false)

    Returns:
        PDFToHTMLResponse with HTML content
    """
    client = get_client()
    try:
        return await client.pdf_to_html(url, pages, simple)
    except PDFcoAPIError as e:
        logger.warning("PDF to HTML conversion failed: %s", e.message)
        raise ToolError(f"PDF to HTML conversion failed: {e.message}") from e


@mcp.tool()
async def pdf_to_csv(
    url: str,
    pages: str | None = None,
) -> PDFToCSVResponse:
    """Extract tables from PDF to CSV.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")

    Returns:
        PDFToCSVResponse with CSV content
    """
    client = get_client()
    try:
        return await client.pdf_to_csv(url, pages)
    except PDFcoAPIError as e:
        logger.warning("PDF to CSV conversion failed: %s", e.message)
        raise ToolError(f"PDF to CSV conversion failed: {e.message}") from e


@mcp.tool()
async def pdf_merge(
    urls: list[str],
    name: str = "merged.pdf",
    async_mode: bool = False,
) -> list[ContentBlock]:
    """Merge multiple PDFs into one.

    Args:
        urls: List of PDF URLs or base64 encoded PDFs
        name: Output filename (default: merged.pdf)
        async_mode: Process asynchronously (default: false)

    Returns:
        ResourceLink to merged PDF and operation metadata
    """
    client = get_client()
    try:
        result = await client.pdf_merge(urls, name, async_mode)
        if result.error or not result.url:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"success": False, "error": result.message or "PDF merge failed"}
                    ),
                ),
            ]
        return [
            ResourceLink(
                type="resource_link",
                uri=result.url,
                name=name,
                mime_type="application/pdf",
            ),
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "pageCount": result.pageCount,
                        "message": result.message,
                    }
                ),
            ),
        ]
    except PDFcoAPIError as e:
        logger.warning("PDF merge failed: %s", e.message)
        raise ToolError(f"PDF merge failed: {e.message}") from e


@mcp.tool()
async def pdf_split(
    url: str,
    pages: str | None = None,
    split_by_pages: bool = False,
) -> PDFSplitResponse:
    """Split PDF into separate pages or ranges.

    Args:
        url: URL or base64 encoded PDF
        pages: Page ranges to extract (e.g., "1-3,5-7")
        split_by_pages: Split into individual pages (default: false)

    Returns:
        PDFSplitResponse with URLs to split PDF files
    """
    client = get_client()
    try:
        return await client.pdf_split(url, pages, split_by_pages)
    except PDFcoAPIError as e:
        logger.warning("PDF split failed: %s", e.message)
        raise ToolError(f"PDF split failed: {e.message}") from e


@mcp.tool()
async def pdf_info(
    url: str,
) -> PDFInfoResponse:
    """Get PDF metadata (pages, size, etc.).

    Args:
        url: URL or base64 encoded PDF

    Returns:
        PDFInfoResponse with PDF metadata
    """
    client = get_client()
    try:
        return await client.pdf_info(url)
    except PDFcoAPIError as e:
        logger.warning("PDF info retrieval failed: %s", e.message)
        raise ToolError(f"PDF info retrieval failed: {e.message}") from e


@mcp.tool()
async def html_to_pdf(
    html: str,
    name: str = "document.pdf",
    margins: str | None = None,
    orientation: str = "Portrait",
    page_size: str = "Letter",
) -> list[ContentBlock]:
    """Convert HTML to PDF.

    Args:
        html: HTML content or URL
        name: Output filename (default: document.pdf)
        margins: Margins in format "top,right,bottom,left" (e.g., "10mm,10mm,10mm,10mm")
        orientation: Portrait or Landscape (default: Portrait)
        page_size: Letter, A4, Legal, etc. (default: Letter)

    Returns:
        ResourceLink to generated PDF and operation metadata
    """
    client = get_client()
    try:
        result = await client.html_to_pdf(html, name, margins, orientation, page_size)
        if result.error or not result.url:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "success": False,
                            "error": result.message or "HTML to PDF conversion failed",
                        }
                    ),
                ),
            ]
        return [
            ResourceLink(
                type="resource_link",
                uri=result.url,
                name=name,
                mime_type="application/pdf",
            ),
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": True,
                        "pageCount": result.pageCount,
                        "message": result.message,
                    }
                ),
            ),
        ]
    except PDFcoAPIError as e:
        logger.warning("HTML to PDF conversion failed: %s", e.message)
        raise ToolError(f"HTML to PDF conversion failed: {e.message}") from e


@mcp.tool()
async def url_to_pdf(
    url: str,
    name: str = "webpage.pdf",
    orientation: str = "Portrait",
    page_size: str = "Letter",
) -> URLToPDFResponse:
    """Convert web page URL to PDF.

    Args:
        url: Web page URL
        name: Output filename (default: webpage.pdf)
        orientation: Portrait or Landscape (default: Portrait)
        page_size: Letter, A4, Legal, etc. (default: Letter)

    Returns:
        URLToPDFResponse with generated PDF URL
    """
    client = get_client()
    try:
        return await client.url_to_pdf(url, name, orientation, page_size)
    except PDFcoAPIError as e:
        logger.warning("URL to PDF conversion failed: %s", e.message)
        raise ToolError(f"URL to PDF conversion failed: {e.message}") from e


@mcp.tool()
async def image_to_pdf(
    images: list[str],
    name: str = "images.pdf",
) -> ImageToPDFResponse:
    """Convert images to PDF.

    Args:
        images: List of image URLs or base64 encoded images
        name: Output filename (default: images.pdf)

    Returns:
        ImageToPDFResponse with generated PDF URL
    """
    client = get_client()
    try:
        return await client.image_to_pdf(images, name)
    except PDFcoAPIError as e:
        logger.warning("Image to PDF conversion failed: %s", e.message)
        raise ToolError(f"Image to PDF conversion failed: {e.message}") from e


@mcp.tool()
async def pdf_add_watermark(
    url: str,
    text: str,
    x: int = 100,
    y: int = 100,
    font_size: int = 24,
    color: str = "FF0000",
    opacity: float = 0.5,
    pages: str = "0-",
    name: str = "watermarked.pdf",
) -> PDFWatermarkResponse:
    """Add text watermark/annotation to PDF.

    Args:
        url: URL or base64 encoded PDF
        text: Watermark text
        x: X position (default: 100)
        y: Y position (default: 100)
        font_size: Font size (default: 24)
        color: Hex color without # (default: FF0000 red)
        opacity: Opacity 0.0-1.0 (default: 0.5)
        pages: Page range to apply watermark (default: "0-" for all pages)
        name: Output filename (default: watermarked.pdf)

    Returns:
        PDFWatermarkResponse with watermarked PDF URL
    """
    client = get_client()
    try:
        return await client.pdf_add_watermark(
            url, text, x, y, font_size, color, opacity, pages, name
        )
    except PDFcoAPIError as e:
        logger.warning("PDF watermark failed: %s", e.message)
        raise ToolError(f"PDF watermark failed: {e.message}") from e


@mcp.tool()
async def pdf_rotate(
    url: str,
    angle: int,
    pages: str | None = None,
) -> PDFRotateResponse:
    """Rotate PDF pages.

    Args:
        url: URL or base64 encoded PDF
        angle: Rotation angle (90, 180, 270, -90)
        pages: Page range (e.g., "1-3")

    Returns:
        PDFRotateResponse with rotated PDF URL
    """
    client = get_client()
    try:
        return await client.pdf_rotate(url, angle, pages)
    except PDFcoAPIError as e:
        logger.warning("PDF rotation failed: %s", e.message)
        raise ToolError(f"PDF rotation failed: {e.message}") from e


@mcp.tool()
async def pdf_compress(
    url: str,
    compression_level: str = "balanced",
) -> PDFCompressResponse:
    """Compress PDF file size.

    Args:
        url: URL or base64 encoded PDF
        compression_level: low, balanced, high, extreme (default: balanced)

    Returns:
        PDFCompressResponse with compressed PDF URL and compression stats
    """
    client = get_client()
    try:
        return await client.pdf_compress(url, compression_level)
    except PDFcoAPIError as e:
        logger.warning("PDF compression failed: %s", e.message)
        raise ToolError(f"PDF compression failed: {e.message}") from e


@mcp.tool()
async def pdf_protect(
    url: str,
    owner_password: str,
    user_password: str | None = None,
    allow_print: bool = True,
    allow_copy: bool = False,
) -> PDFProtectResponse:
    """Add password protection to PDF.

    Args:
        url: URL or base64 encoded PDF
        owner_password: Owner password for full access
        user_password: User password for restricted access (optional)
        allow_print: Allow printing (default: true)
        allow_copy: Allow copying text (default: false)

    Returns:
        PDFProtectResponse with protected PDF URL
    """
    client = get_client()
    try:
        return await client.pdf_protect(url, owner_password, user_password, allow_print, allow_copy)
    except PDFcoAPIError as e:
        logger.warning("PDF protection failed: %s", e.message)
        raise ToolError(f"PDF protection failed: {e.message}") from e


@mcp.tool()
async def pdf_unlock(
    url: str,
    password: str,
) -> PDFUnlockResponse:
    """Remove password from PDF.

    Args:
        url: URL or base64 encoded PDF
        password: PDF password

    Returns:
        PDFUnlockResponse with unlocked PDF URL
    """
    client = get_client()
    try:
        return await client.pdf_unlock(url, password)
    except PDFcoAPIError as e:
        logger.warning("PDF unlock failed: %s", e.message)
        raise ToolError(f"PDF unlock failed: {e.message}") from e


@mcp.tool()
async def barcode_generate(
    value: str,
    barcode_type: str = "QRCode",
    format: str = "png",
) -> BarcodeGenerateResponse:
    """Generate barcode images.

    Args:
        value: Barcode value/text
        barcode_type: QRCode, Code128, Code39, EAN13, etc. (default: QRCode)
        format: png, jpg, svg (default: png)

    Returns:
        BarcodeGenerateResponse with generated barcode image URL
    """
    client = get_client()
    try:
        return await client.barcode_generate(value, barcode_type, format)
    except PDFcoAPIError as e:
        logger.warning("Barcode generation failed: %s", e.message)
        raise ToolError(f"Barcode generation failed: {e.message}") from e


@mcp.tool()
async def barcode_read(
    url: str,
    barcode_types: list[str] | None = None,
) -> BarcodeReadResponse:
    """Read barcodes from images.

    Args:
        url: Image URL or base64 encoded image
        barcode_types: List of barcode types to detect (default: all common types)

    Returns:
        BarcodeReadResponse with detected barcodes
    """
    client = get_client()
    try:
        # If no types specified, use all common barcode types
        if barcode_types is None:
            barcode_types = ["QRCode", "Code128", "Code39", "EAN13", "EAN8", "UPCA", "UPCE"]
        return await client.barcode_read(url, barcode_types)
    except PDFcoAPIError as e:
        logger.warning("Barcode reading failed: %s", e.message)
        raise ToolError(f"Barcode reading failed: {e.message}") from e


@mcp.tool()
async def ocr_pdf(
    url: str,
    pages: str | None = None,
    lang: str = "eng",
) -> OCRPDFResponse:
    """OCR scanned PDFs to searchable text.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        lang: Language code (eng, spa, fra, deu, etc.) (default: eng)

    Returns:
        OCRPDFResponse with OCR'd PDF URL and extracted text
    """
    client = get_client()
    try:
        return await client.ocr_pdf(url, pages, lang)
    except PDFcoAPIError as e:
        logger.warning("PDF OCR failed: %s", e.message)
        raise ToolError(f"PDF OCR failed: {e.message}") from e


# Create ASGI application for deployment
app = mcp.http_app()

# Stdio entrypoint for Claude Desktop / mpak
if __name__ == "__main__":
    mcp.run()
