"""FastMCP server for PDF.co API."""

import os
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ResourceLink

from .api_client import PDFcoAPIError, PDFcoClient
from .api_models import (
    BarcodeGenerateResponse,
    BarcodeReadResponse,
    PDFInfoResponse,
    PDFToCSVResponse,
    PDFToHTMLResponse,
    PDFToJSONResponse,
    PDFToTextResponse,
)

# Create MCP server
mcp = FastMCP("PDFco")

# Global client instance
_client: PDFcoClient | None = None


async def get_client(ctx: Context[Any, Any, Any]) -> PDFcoClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        api_key = os.environ.get("PDFCO_API_KEY")
        if not api_key:
            await ctx.warning(
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
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> PDFToTextResponse:
    """Extract text from PDF.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3" or "1,3,5")
        async_mode: Process asynchronously (default: false)
        ctx: MCP context

    Returns:
        PDFToTextResponse with extracted text content
    """
    client = await get_client(ctx)
    try:
        return await client.pdf_to_text(url, pages, async_mode)
    except PDFcoAPIError as e:
        await ctx.error(f"PDF to text conversion failed: {e.message}")
        raise


@mcp.tool()
async def pdf_to_json(
    url: str,
    pages: str | None = None,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> PDFToJSONResponse:
    """Extract structured data from PDF.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        ctx: MCP context

    Returns:
        PDFToJSONResponse with structured data
    """
    client = await get_client(ctx)
    try:
        return await client.pdf_to_json(url, pages)
    except PDFcoAPIError as e:
        await ctx.error(f"PDF to JSON conversion failed: {e.message}")
        raise


@mcp.tool()
async def pdf_to_html(
    url: str,
    pages: str | None = None,
    simple: bool = False,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> PDFToHTMLResponse:
    """Convert PDF to HTML.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        simple: Use simple HTML mode (default: false)
        ctx: MCP context

    Returns:
        PDFToHTMLResponse with HTML content
    """
    client = await get_client(ctx)
    try:
        return await client.pdf_to_html(url, pages, simple)
    except PDFcoAPIError as e:
        await ctx.error(f"PDF to HTML conversion failed: {e.message}")
        raise


@mcp.tool()
async def pdf_to_csv(
    url: str,
    pages: str | None = None,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> PDFToCSVResponse:
    """Extract tables from PDF to CSV.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        ctx: MCP context

    Returns:
        PDFToCSVResponse with CSV content
    """
    client = await get_client(ctx)
    try:
        return await client.pdf_to_csv(url, pages)
    except PDFcoAPIError as e:
        await ctx.error(f"PDF to CSV conversion failed: {e.message}")
        raise


@mcp.tool()
async def pdf_merge(
    urls: list[str],
    name: str = "merged.pdf",
    async_mode: bool = False,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Merge multiple PDFs into one.

    Args:
        urls: List of PDF URLs or base64 encoded PDFs
        name: Output filename (default: merged.pdf)
        async_mode: Process asynchronously (default: false)
        ctx: MCP context

    Returns:
        ResourceLink to the merged PDF with pageCount in meta
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_merge(urls, name, async_mode)
        meta: dict[str, Any] = {}
        if response.pageCount:
            meta["pageCount"] = response.pageCount
        return ResourceLink(
            type="resource_link",
            name=name,
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf",
            _meta=meta if meta else None
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF merge failed: {e.message}")
        raise


@mcp.tool()
async def pdf_split(
    url: str,
    pages: str | None = None,
    split_by_pages: bool = False,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> list[ResourceLink]:
    """Split PDF into separate pages or ranges.

    Args:
        url: URL or base64 encoded PDF
        pages: Page ranges to extract (e.g., "1-3,5-7")
        split_by_pages: Split into individual pages (default: false)
        ctx: MCP context

    Returns:
        List of ResourceLinks to the split PDF files
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_split(url, pages, split_by_pages)
        resources = []
        if response.urls:
            for idx, pdf_url in enumerate(response.urls, 1):
                resources.append(ResourceLink(
                    type="resource_link",
                    name=f"split-{idx}.pdf",
                    uri=pdf_url,  # type: ignore[arg-type]
                    mimeType="application/pdf"
                ))
        return resources
    except PDFcoAPIError as e:
        await ctx.error(f"PDF split failed: {e.message}")
        raise


@mcp.tool()
async def pdf_info(
    url: str,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> PDFInfoResponse:
    """Get PDF metadata (pages, size, etc.).

    Args:
        url: URL or base64 encoded PDF
        ctx: MCP context

    Returns:
        PDFInfoResponse with PDF metadata
    """
    client = await get_client(ctx)
    try:
        return await client.pdf_info(url)
    except PDFcoAPIError as e:
        await ctx.error(f"PDF info retrieval failed: {e.message}")
        raise


@mcp.tool()
async def html_to_pdf(
    html: str,
    name: str = "document.pdf",
    margins: str | None = None,
    orientation: str = "Portrait",
    page_size: str = "Letter",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Convert HTML to PDF.

    Args:
        html: HTML content or URL
        name: Output filename (default: document.pdf)
        margins: Margins in format "top,right,bottom,left" (e.g., "10mm,10mm,10mm,10mm")
        orientation: Portrait or Landscape (default: Portrait)
        page_size: Letter, A4, Legal, etc. (default: Letter)
        ctx: MCP context

    Returns:
        ResourceLink to the generated PDF
    """
    client = await get_client(ctx)
    try:
        response = await client.html_to_pdf(html, name, margins, orientation, page_size)
        return ResourceLink(
            type="resource_link",
            name=name,
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf"
        )
    except PDFcoAPIError as e:
        await ctx.error(f"HTML to PDF conversion failed: {e.message}")
        raise


@mcp.tool()
async def url_to_pdf(
    url: str,
    name: str = "webpage.pdf",
    orientation: str = "Portrait",
    page_size: str = "Letter",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Convert web page URL to PDF.

    Args:
        url: Web page URL
        name: Output filename (default: webpage.pdf)
        orientation: Portrait or Landscape (default: Portrait)
        page_size: Letter, A4, Legal, etc. (default: Letter)
        ctx: MCP context

    Returns:
        ResourceLink to the generated PDF with pageCount in meta
    """
    client = await get_client(ctx)
    try:
        response = await client.url_to_pdf(url, name, orientation, page_size)
        meta: dict[str, Any] = {}
        if response.pageCount:
            meta["pageCount"] = response.pageCount
        return ResourceLink(
            type="resource_link",
            name=name,
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf",
            _meta=meta if meta else None
        )
    except PDFcoAPIError as e:
        await ctx.error(f"URL to PDF conversion failed: {e.message}")
        raise


@mcp.tool()
async def image_to_pdf(
    images: list[str],
    name: str = "images.pdf",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Convert images to PDF.

    Args:
        images: List of image URLs or base64 encoded images
        name: Output filename (default: images.pdf)
        ctx: MCP context

    Returns:
        ResourceLink to the generated PDF with pageCount in meta
    """
    client = await get_client(ctx)
    try:
        response = await client.image_to_pdf(images, name)
        meta: dict[str, Any] = {}
        if response.pageCount:
            meta["pageCount"] = response.pageCount
        return ResourceLink(
            type="resource_link",
            name=name,
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf",
            _meta=meta if meta else None
        )
    except PDFcoAPIError as e:
        await ctx.error(f"Image to PDF conversion failed: {e.message}")
        raise


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
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
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
        ctx: MCP context

    Returns:
        ResourceLink to the watermarked PDF
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_add_watermark(
            url, text, x, y, font_size, color, opacity, pages, name
        )
        return ResourceLink(
            type="resource_link",
            name=name,
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf"
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF watermark failed: {e.message}")
        raise


@mcp.tool()
async def pdf_rotate(
    url: str,
    angle: int,
    pages: str | None = None,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Rotate PDF pages.

    Args:
        url: URL or base64 encoded PDF
        angle: Rotation angle (90, 180, 270, -90)
        pages: Page range (e.g., "1-3")
        ctx: MCP context

    Returns:
        ResourceLink to the rotated PDF
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_rotate(url, angle, pages)
        return ResourceLink(
            type="resource_link",
            name="rotated.pdf",
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf"
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF rotation failed: {e.message}")
        raise


@mcp.tool()
async def pdf_compress(
    url: str,
    compression_level: str = "balanced",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Compress PDF file size.

    Args:
        url: URL or base64 encoded PDF
        compression_level: low, balanced, high, extreme (default: balanced)
        ctx: MCP context

    Returns:
        ResourceLink to the compressed PDF with compression stats in meta
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_compress(url, compression_level)
        meta: dict[str, Any] = {}
        if response.originalSize:
            meta["originalSize"] = response.originalSize
        if response.compressedSize:
            meta["compressedSize"] = response.compressedSize
        if response.compressionRatio:
            meta["compressionRatio"] = response.compressionRatio
        return ResourceLink(
            type="resource_link",
            name="compressed.pdf",
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf",
            size=int(response.compressedSize) if response.compressedSize else None,
            _meta=meta if meta else None
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF compression failed: {e.message}")
        raise


@mcp.tool()
async def pdf_protect(
    url: str,
    owner_password: str,
    user_password: str | None = None,
    allow_print: bool = True,
    allow_copy: bool = False,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Add password protection to PDF.

    Args:
        url: URL or base64 encoded PDF
        owner_password: Owner password for full access
        user_password: User password for restricted access (optional)
        allow_print: Allow printing (default: true)
        allow_copy: Allow copying text (default: false)
        ctx: MCP context

    Returns:
        ResourceLink to the protected PDF
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_protect(url, owner_password, user_password, allow_print, allow_copy)
        return ResourceLink(
            type="resource_link",
            name="protected.pdf",
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf"
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF protection failed: {e.message}")
        raise


@mcp.tool()
async def pdf_unlock(
    url: str,
    password: str,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """Remove password from PDF.

    Args:
        url: URL or base64 encoded PDF
        password: PDF password
        ctx: MCP context

    Returns:
        ResourceLink to the unlocked PDF
    """
    client = await get_client(ctx)
    try:
        response = await client.pdf_unlock(url, password)
        return ResourceLink(
            type="resource_link",
            name="unlocked.pdf",
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf"
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF unlock failed: {e.message}")
        raise


@mcp.tool()
async def barcode_generate(
    value: str,
    barcode_type: str = "QRCode",
    format: str = "png",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> BarcodeGenerateResponse:
    """Generate barcode images.

    Args:
        value: Barcode value/text
        barcode_type: QRCode, Code128, Code39, EAN13, etc. (default: QRCode)
        format: png, jpg, svg (default: png)
        ctx: MCP context

    Returns:
        BarcodeGenerateResponse with generated barcode image URL
    """
    client = await get_client(ctx)
    try:
        return await client.barcode_generate(value, barcode_type, format)
    except PDFcoAPIError as e:
        await ctx.error(f"Barcode generation failed: {e.message}")
        raise


@mcp.tool()
async def barcode_read(
    url: str,
    barcode_types: list[str] | None = None,
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> BarcodeReadResponse:
    """Read barcodes from images.

    Args:
        url: Image URL or base64 encoded image
        barcode_types: List of barcode types to detect (default: all common types)
        ctx: MCP context

    Returns:
        BarcodeReadResponse with detected barcodes
    """
    client = await get_client(ctx)
    try:
        # If no types specified, use all common barcode types
        if barcode_types is None:
            barcode_types = ["QRCode", "Code128", "Code39", "EAN13", "EAN8", "UPCA", "UPCE"]
        return await client.barcode_read(url, barcode_types)
    except PDFcoAPIError as e:
        await ctx.error(f"Barcode reading failed: {e.message}")
        raise


@mcp.tool()
async def ocr_pdf(
    url: str,
    pages: str | None = None,
    lang: str = "eng",
    ctx: Context[Any, Any, Any] = None,  # type: ignore[assignment]
) -> ResourceLink:
    """OCR scanned PDFs to searchable text.

    Args:
        url: URL or base64 encoded PDF
        pages: Page range (e.g., "1-3")
        lang: Language code (eng, spa, fra, deu, etc.) (default: eng)
        ctx: MCP context

    Returns:
        ResourceLink to the OCR'd PDF with extracted text and pageCount in meta
    """
    client = await get_client(ctx)
    try:
        response = await client.ocr_pdf(url, pages, lang)
        meta: dict[str, Any] = {}
        if response.text:
            meta["text"] = response.text
        if response.pageCount:
            meta["pageCount"] = response.pageCount
        return ResourceLink(
            type="resource_link",
            name="ocr.pdf",
            uri=response.url,  # type: ignore[arg-type]
            mimeType="application/pdf",
            _meta=meta if meta else None
        )
    except PDFcoAPIError as e:
        await ctx.error(f"PDF OCR failed: {e.message}")
        raise


# Create ASGI application for uvicorn
app = mcp.streamable_http_app()

