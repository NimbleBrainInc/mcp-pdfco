"""Async API client for PDF.co API."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError

from .api_models import (
    BarcodeGenerateResponse,
    BarcodeReadResponse,
    HTMLToPDFResponse,
    ImageToPDFResponse,
    OCRPDFResponse,
    PDFCompressResponse,
    PDFInfoResponse,
    PDFMergeResponse,
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


class PDFcoAPIError(Exception):
    """Custom exception for PDF.co API errors."""

    def __init__(
        self, status: int, message: str, details: dict[str, Any] | None = None
    ) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"PDF.co API Error {status}: {message}")


class PDFcoClient:
    """Async API client for PDF.co API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.pdf.co/v1",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("PDFCO_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "PDFcoClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> None:
        """Create session if it doesn't exist."""
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-pdfco/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["x-api-key"] = self.api_key

            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: Any | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with error handling."""
        await self._ensure_session()

        url = f"{self.base_url}{path}"

        kwargs: dict[str, Any] = {}
        if json_data is not None:
            kwargs["json"] = json_data

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            async with self._session.request(
                method, url, params=params, **kwargs
            ) as response:
                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    result = await response.json()
                else:
                    text = await response.text()
                    # Try to parse as JSON
                    if text.startswith("{") or text.startswith("["):
                        import json

                        try:
                            result = json.loads(text)
                        except json.JSONDecodeError:
                            result = {"result": text}
                    else:
                        result = {"result": text}

                # Check for errors in response
                if response.status >= 400:
                    error_msg = "Unknown error"
                    if isinstance(result, dict):
                        error_msg = (
                            result.get("message")
                            or result.get("error", {}).get("message")
                            or str(result.get("error", error_msg))
                        )
                    raise PDFcoAPIError(response.status, error_msg, result)

                # Check for API-level errors
                if isinstance(result, dict) and result.get("error") is True:
                    error_msg = result.get("message", "API returned error flag")
                    raise PDFcoAPIError(
                        response.status or 500, error_msg, result
                    )

                return result  # type: ignore[no-any-return]

        except ClientError as e:
            raise PDFcoAPIError(500, f"Network error: {str(e)}") from e

    async def _fetch_content(self, url: str) -> str | dict[str, Any]:
        """Fetch content from a URL (typically an S3 URL returned by PDF.co).

        Args:
            url: The URL to fetch content from

        Returns:
            The content as a string or parsed JSON dict

        Raises:
            PDFcoAPIError: If fetching fails
        """
        await self._ensure_session()

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            async with self._session.get(url) as response:
                if response.status >= 400:
                    raise PDFcoAPIError(
                        response.status,
                        f"Failed to fetch content from {url}",
                        {"url": url}
                    )

                content_type = response.headers.get("Content-Type", "")

                # If it's JSON, parse it
                if "application/json" in content_type:
                    return await response.json()  # type: ignore[no-any-return]
                else:
                    # Return as text for HTML, CSV, plain text
                    return await response.text()

        except ClientError as e:
            raise PDFcoAPIError(
                500,
                f"Network error fetching content from {url}: {str(e)}"
            ) from e

    async def pdf_to_text(
        self, url: str, pages: str | None = None, async_mode: bool = False
    ) -> PDFToTextResponse:
        """Extract text from PDF."""
        payload: dict[str, Any] = {"url": url, "async": async_mode}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/convert/to/text", json_data=payload)
        response = PDFToTextResponse(**data)

        # If API returned a URL but no text content, fetch it
        if response.url and not response.text and not response.error:
            try:
                content = await self._fetch_content(response.url)
                if isinstance(content, str):
                    response.text = content
            except PDFcoAPIError:
                # If fetching fails, leave the URL for the user to fetch manually
                pass

        return response

    async def pdf_to_json(
        self, url: str, pages: str | None = None
    ) -> PDFToJSONResponse:
        """Extract structured data from PDF."""
        payload: dict[str, Any] = {"url": url}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/convert/to/json", json_data=payload)
        response = PDFToJSONResponse(**data)

        # If API returned a URL but no data content, fetch it
        if response.url and not response.data and not response.error:
            try:
                content = await self._fetch_content(response.url)
                if isinstance(content, dict):
                    response.data = content
            except PDFcoAPIError:
                # If fetching fails, leave the URL for the user to fetch manually
                pass

        return response

    async def pdf_to_html(
        self, url: str, pages: str | None = None, simple: bool = False
    ) -> PDFToHTMLResponse:
        """Convert PDF to HTML."""
        payload: dict[str, Any] = {"url": url, "simple": simple}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/convert/to/html", json_data=payload)
        response = PDFToHTMLResponse(**data)

        # If API returned a URL but no html content, fetch it
        if response.url and not response.html and not response.error:
            try:
                content = await self._fetch_content(response.url)
                if isinstance(content, str):
                    response.html = content
            except PDFcoAPIError:
                # If fetching fails, leave the URL for the user to fetch manually
                pass

        return response

    async def pdf_to_csv(
        self, url: str, pages: str | None = None
    ) -> PDFToCSVResponse:
        """Extract tables from PDF to CSV."""
        payload: dict[str, Any] = {"url": url}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/convert/to/csv", json_data=payload)
        response = PDFToCSVResponse(**data)

        # If API returned a URL but no csv content, fetch it
        if response.url and not response.csv and not response.error:
            try:
                content = await self._fetch_content(response.url)
                if isinstance(content, str):
                    response.csv = content
            except PDFcoAPIError:
                # If fetching fails, leave the URL for the user to fetch manually
                pass

        return response

    async def pdf_merge(
        self, urls: list[str], name: str = "merged.pdf", async_mode: bool = False
    ) -> PDFMergeResponse:
        """Merge multiple PDFs into one."""
        payload = {"url": ",".join(urls), "name": name, "async": async_mode}

        data = await self._request("POST", "/pdf/merge", json_data=payload)
        return PDFMergeResponse(**data)

    async def pdf_split(
        self, url: str, pages: str | None = None, split_by_pages: bool = False
    ) -> PDFSplitResponse:
        """Split PDF into separate pages or ranges."""
        payload: dict[str, Any] = {"url": url}
        if pages:
            payload["pages"] = pages
        if split_by_pages:
            payload["splitByPages"] = True

        data = await self._request("POST", "/pdf/split", json_data=payload)
        return PDFSplitResponse(**data)

    async def pdf_info(self, url: str) -> PDFInfoResponse:
        """Get PDF metadata (pages, size, etc.)."""
        payload = {"url": url}

        data = await self._request("POST", "/pdf/info", json_data=payload)
        return PDFInfoResponse(**data)

    async def html_to_pdf(
        self,
        html: str,
        name: str = "document.pdf",
        margins: str | None = None,
        orientation: str = "Portrait",
        page_size: str = "Letter",
    ) -> HTMLToPDFResponse:
        """Convert HTML to PDF."""
        payload: dict[str, Any] = {
            "html": html,
            "name": name,
            "orientation": orientation,
            "pageSize": page_size,
        }
        if margins:
            payload["margins"] = margins

        data = await self._request(
            "POST", "/pdf/convert/from/html", json_data=payload
        )
        return HTMLToPDFResponse(**data)

    async def url_to_pdf(
        self,
        url: str,
        name: str = "webpage.pdf",
        orientation: str = "Portrait",
        page_size: str = "Letter",
    ) -> URLToPDFResponse:
        """Convert web page URL to PDF."""
        payload = {
            "url": url,
            "name": name,
            "orientation": orientation,
            "pageSize": page_size,
        }

        data = await self._request("POST", "/pdf/convert/from/url", json_data=payload)
        return URLToPDFResponse(**data)

    async def image_to_pdf(
        self, images: list[str], name: str = "images.pdf"
    ) -> ImageToPDFResponse:
        """Convert images to PDF."""
        payload = {"url": ",".join(images), "name": name}

        data = await self._request(
            "POST", "/pdf/convert/from/image", json_data=payload
        )
        return ImageToPDFResponse(**data)

    async def pdf_add_watermark(
        self,
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
        """Add text watermark/annotation to PDF using the PDF Edit Add endpoint.

        Args:
            url: URL to the source PDF file
            text: Text to add as watermark
            x: X coordinate position
            y: Y coordinate position
            font_size: Font size for the text
            color: Hex color code without # (e.g., FF0000 for red)
            opacity: Opacity value 0.0-1.0 (will be converted to alpha channel)
            pages: Page range (default: "0-" for all pages)
            name: Output filename (default: "watermarked.pdf")

        Returns:
            PDFWatermarkResponse with URL to the watermarked PDF
        """
        # Convert opacity (0.0-1.0) to alpha channel (00-FF)
        # PDF.co uses AARRGGBB format where AA is the alpha channel
        alpha = int(opacity * 255)
        alpha_hex = f"{alpha:02X}"

        # Combine alpha with color to create AARRGGBB format
        color_with_alpha = f"{alpha_hex}{color}"

        payload = {
            "url": url,
            "name": name,
            "annotations": [
                {
                    "text": text,
                    "x": x,
                    "y": y,
                    "size": font_size,
                    "color": color_with_alpha,
                    "pages": pages,
                }
            ],
        }

        data = await self._request("POST", "/pdf/edit/add", json_data=payload)
        return PDFWatermarkResponse(**data)

    async def pdf_rotate(
        self, url: str, angle: int, pages: str | None = None
    ) -> PDFRotateResponse:
        """Rotate PDF pages."""
        payload: dict[str, Any] = {"url": url, "angle": angle}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/edit/rotate", json_data=payload)
        return PDFRotateResponse(**data)

    async def pdf_compress(
        self, url: str, compression_level: str = "balanced"
    ) -> PDFCompressResponse:
        """Compress PDF file size."""
        payload = {"url": url, "compressionLevel": compression_level}

        data = await self._request("POST", "/pdf/optimize", json_data=payload)
        return PDFCompressResponse(**data)

    async def pdf_protect(
        self,
        url: str,
        owner_password: str,
        user_password: str | None = None,
        allow_print: bool = True,
        allow_copy: bool = False,
    ) -> PDFProtectResponse:
        """Add password protection to PDF."""
        payload: dict[str, Any] = {
            "url": url,
            "ownerPassword": owner_password,
            "allowPrint": allow_print,
            "allowCopy": allow_copy,
        }
        if user_password:
            payload["userPassword"] = user_password

        data = await self._request("POST", "/pdf/security/add", json_data=payload)
        return PDFProtectResponse(**data)

    async def pdf_unlock(self, url: str, password: str) -> PDFUnlockResponse:
        """Remove password from PDF."""
        payload = {"url": url, "password": password}

        data = await self._request("POST", "/pdf/security/remove", json_data=payload)
        return PDFUnlockResponse(**data)

    async def barcode_generate(
        self, value: str, barcode_type: str = "QRCode", format: str = "png"
    ) -> BarcodeGenerateResponse:
        """Generate barcode images."""
        payload = {"value": value, "type": barcode_type, "format": format}

        data = await self._request("POST", "/barcode/generate", json_data=payload)
        return BarcodeGenerateResponse(**data)

    async def barcode_read(
        self, url: str, barcode_types: list[str] | None = None
    ) -> BarcodeReadResponse:
        """Read barcodes from images."""
        payload: dict[str, Any] = {"url": url}
        if barcode_types:
            payload["types"] = ",".join(barcode_types)

        data = await self._request("POST", "/barcode/read/from/url", json_data=payload)
        return BarcodeReadResponse(**data)

    async def ocr_pdf(
        self, url: str, pages: str | None = None, lang: str = "eng"
    ) -> OCRPDFResponse:
        """OCR scanned PDFs to searchable text."""
        payload: dict[str, Any] = {"url": url, "lang": lang}
        if pages:
            payload["pages"] = pages

        data = await self._request("POST", "/pdf/ocr", json_data=payload)
        return OCRPDFResponse(**data)
