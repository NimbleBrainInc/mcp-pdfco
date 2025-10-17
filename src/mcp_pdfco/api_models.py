"""Pydantic models for PDF.co API responses."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CompressionLevel(str, Enum):
    """Enum for PDF compression levels."""

    LOW = "low"
    BALANCED = "balanced"
    HIGH = "high"
    EXTREME = "extreme"


class Orientation(str, Enum):
    """Enum for page orientation."""

    PORTRAIT = "Portrait"
    LANDSCAPE = "Landscape"


class PageSize(str, Enum):
    """Enum for page sizes."""

    LETTER = "Letter"
    A4 = "A4"
    LEGAL = "Legal"


class BarcodeType(str, Enum):
    """Enum for barcode types."""

    QRCODE = "QRCode"
    CODE128 = "Code128"
    CODE39 = "Code39"
    EAN13 = "EAN13"
    EAN8 = "EAN8"
    UPCA = "UPCA"
    UPCE = "UPCE"


class BarcodeFormat(str, Enum):
    """Enum for barcode output formats."""

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"


class PDFToTextResponse(BaseModel):
    """Response model for PDF to text conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the output file")
    text: str | None = Field(None, description="Extracted text content")
    pageCount: int | None = Field(None, description="Number of pages processed")
    message: str | None = Field(None, description="Error or status message")


class PDFToJSONResponse(BaseModel):
    """Response model for PDF to JSON conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the output JSON file")
    data: dict[str, Any] | None = Field(None, description="Extracted structured data")
    pageCount: int | None = Field(None, description="Number of pages processed")
    message: str | None = Field(None, description="Error or status message")


class PDFToHTMLResponse(BaseModel):
    """Response model for PDF to HTML conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the output HTML file")
    html: str | None = Field(None, description="HTML content")
    pageCount: int | None = Field(None, description="Number of pages processed")
    message: str | None = Field(None, description="Error or status message")


class PDFToCSVResponse(BaseModel):
    """Response model for PDF to CSV conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the output CSV file")
    csv: str | None = Field(None, description="CSV content")
    pageCount: int | None = Field(None, description="Number of pages processed")
    message: str | None = Field(None, description="Error or status message")


class PDFMergeResponse(BaseModel):
    """Response model for PDF merge operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the merged PDF")
    pageCount: int | None = Field(None, description="Total number of pages in merged PDF")
    message: str | None = Field(None, description="Error or status message")


class PDFSplitResponse(BaseModel):
    """Response model for PDF split operation."""

    error: bool = Field(..., description="Whether an error occurred")
    urls: list[str] | None = Field(None, description="URLs to the split PDF files")
    pageCount: int | None = Field(None, description="Number of output files created")
    message: str | None = Field(None, description="Error or status message")


class PDFPageRectangle(BaseModel):
    """Model for PDF page rectangle dimensions."""

    Width: float | None = Field(None, description="Page width in points")
    Height: float | None = Field(None, description="Page height in points")


class PDFInfoDetails(BaseModel):
    """Model for PDF info details."""

    PageCount: int | None = Field(None, description="Number of pages in the PDF")
    PageRectangle: PDFPageRectangle | None = Field(None, description="Page dimensions")
    Encrypted: bool | None = Field(None, description="Whether the PDF is encrypted")
    Title: str | None = Field(None, description="PDF title metadata")
    Author: str | None = Field(None, description="PDF author metadata")
    Subject: str | None = Field(None, description="PDF subject metadata")
    FileSize: int | None = Field(None, description="File size in bytes")


class PDFInfoResponse(BaseModel):
    """Response model for PDF info operation."""

    error: bool = Field(..., description="Whether an error occurred")
    info: PDFInfoDetails | None = Field(None, description="PDF information details")
    message: str | None = Field(None, description="Error or status message")

    # Convenience properties for backward compatibility
    @property
    def pageCount(self) -> int | None:
        """Get page count."""
        return self.info.PageCount if self.info else None

    @property
    def width(self) -> float | None:
        """Get page width."""
        return self.info.PageRectangle.Width if self.info and self.info.PageRectangle else None

    @property
    def height(self) -> float | None:
        """Get page height."""
        return self.info.PageRectangle.Height if self.info and self.info.PageRectangle else None

    @property
    def fileSize(self) -> int | None:
        """Get file size."""
        return self.info.FileSize if self.info else None

    @property
    def encrypted(self) -> bool | None:
        """Get encrypted status."""
        return self.info.Encrypted if self.info else None

    @property
    def title(self) -> str | None:
        """Get PDF title."""
        return self.info.Title if self.info else None

    @property
    def author(self) -> str | None:
        """Get PDF author."""
        return self.info.Author if self.info else None

    @property
    def subject(self) -> str | None:
        """Get PDF subject."""
        return self.info.Subject if self.info else None


class HTMLToPDFResponse(BaseModel):
    """Response model for HTML to PDF conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the generated PDF")
    pageCount: int | None = Field(None, description="Number of pages in the PDF")
    message: str | None = Field(None, description="Error or status message")


class URLToPDFResponse(BaseModel):
    """Response model for URL to PDF conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the generated PDF")
    pageCount: int | None = Field(None, description="Number of pages in the PDF")
    message: str | None = Field(None, description="Error or status message")


class ImageToPDFResponse(BaseModel):
    """Response model for image to PDF conversion."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the generated PDF")
    pageCount: int | None = Field(None, description="Number of pages in the PDF")
    message: str | None = Field(None, description="Error or status message")


class PDFWatermarkResponse(BaseModel):
    """Response model for PDF watermark operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the watermarked PDF")
    message: str | None = Field(None, description="Error or status message")


class PDFRotateResponse(BaseModel):
    """Response model for PDF rotate operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the rotated PDF")
    message: str | None = Field(None, description="Error or status message")


class PDFCompressResponse(BaseModel):
    """Response model for PDF compression operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the compressed PDF")
    originalSize: int | None = Field(None, description="Original file size in bytes")
    compressedSize: int | None = Field(None, description="Compressed file size in bytes")
    compressionRatio: float | None = Field(None, description="Compression ratio percentage")
    message: str | None = Field(None, description="Error or status message")


class PDFProtectResponse(BaseModel):
    """Response model for PDF protection operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the protected PDF")
    message: str | None = Field(None, description="Error or status message")


class PDFUnlockResponse(BaseModel):
    """Response model for PDF unlock operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the unlocked PDF")
    message: str | None = Field(None, description="Error or status message")


class BarcodeGenerateResponse(BaseModel):
    """Response model for barcode generation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the generated barcode image")
    message: str | None = Field(None, description="Error or status message")


class BarcodeInfo(BaseModel):
    """Model for individual barcode detection result."""

    type: str = Field(..., description="Barcode type (QRCode, Code128, etc.)")
    value: str = Field(..., description="Decoded barcode value")
    confidence: float | None = Field(None, description="Detection confidence score")
    x: int | None = Field(None, description="X coordinate of barcode")
    y: int | None = Field(None, description="Y coordinate of barcode")
    width: int | None = Field(None, description="Width of barcode")
    height: int | None = Field(None, description="Height of barcode")


class BarcodeReadResponse(BaseModel):
    """Response model for barcode reading."""

    error: bool = Field(..., description="Whether an error occurred")
    barcodes: list[BarcodeInfo] | None = Field(None, description="List of detected barcodes")
    message: str | None = Field(None, description="Error or status message")


class OCRPDFResponse(BaseModel):
    """Response model for PDF OCR operation."""

    error: bool = Field(..., description="Whether an error occurred")
    url: str | None = Field(None, description="URL to the OCR'd PDF")
    text: str | None = Field(None, description="Extracted text from OCR")
    pageCount: int | None = Field(None, description="Number of pages processed")
    message: str | None = Field(None, description="Error or status message")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: bool = Field(True, description="Error flag")
    status: int | None = Field(None, description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
