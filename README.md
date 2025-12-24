# MCP Server PDF.co

[![NimbleTools Registry](https://img.shields.io/badge/NimbleTools-Registry-green)](https://github.com/nimbletoolsinc/mcp-registry)
[![NimbleBrain Platform](https://img.shields.io/badge/NimbleBrain-Platform-blue)](https://www.nimblebrain.ai)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://www.nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-pdfco&utm_content=discord-badge)


[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/NimbleBrainInc/mcp-pdfco/actions/workflows/ci.yaml/badge.svg)](https://github.com/NimbleBrainInc/mcp-pdfco/actions)

## About

MCP server for PDF.co API. Comprehensive PDF manipulation, conversion, OCR,
text extraction, and document automation with support for barcodes,
watermarks, and security features.

## Features

- **Full API Coverage**: Complete implementation of PDF.co API endpoints
- **Strongly Typed**: All responses use Pydantic models for type safety
- **S-Tier Architecture**: Production-ready with separated concerns (API client, models, server)
- **HTTP Transport**: Supports streamable-http with health endpoint
- **Async/Await**: Built on aiohttp for high performance
- **Type Safe**: Full mypy strict mode compliance
- **Comprehensive Testing**: Unit tests with pytest and AsyncMock
- **Docker Ready**: Production Dockerfile included

## Available Tools

### PDF Conversion Tools

- `pdf_to_text` - Extract text content from PDF documents
- `pdf_to_json` - Extract structured data from PDFs
- `pdf_to_html` - Convert PDF to HTML format
- `pdf_to_csv` - Extract tables from PDF to CSV

### PDF Manipulation Tools

- `pdf_merge` - Combine multiple PDFs into one
- `pdf_split` - Split PDF into separate pages or ranges
- `pdf_rotate` - Rotate pages in a PDF document
- `pdf_compress` - Reduce PDF file size with configurable compression
- `pdf_add_watermark` - Add text watermarks to PDFs

### PDF Security Tools

- `pdf_protect` - Add password protection to PDFs
- `pdf_unlock` - Remove password protection from PDFs

### PDF Information

- `pdf_info` - Get PDF metadata (pages, size, dimensions, etc.)

### Document Creation Tools

- `html_to_pdf` - Convert HTML content to PDF
- `url_to_pdf` - Convert web pages to PDF
- `image_to_pdf` - Convert images to PDF documents

### Barcode Tools

- `barcode_generate` - Generate QR codes and barcodes
- `barcode_read` - Read and decode barcodes from images

### OCR Tools

- `ocr_pdf` - OCR scanned PDFs to make them searchable

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mcp-pdfco

# Install with uv
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install -e .
```

## Configuration

### API Key

Get your free API key from [PDF.co Dashboard](https://app.pdf.co/dashboard) and set it as an environment variable:

```bash
export PDFCO_API_KEY=your_api_key_here
```

Or create a `.env` file:

```env
PDFCO_API_KEY=your_api_key_here
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pdfco": {
      "command": "uvx",
      "args": ["mcp-pdfco"],
      "env": {
        "PDFCO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Running the Server

### Development Mode

```bash
# Using Python module
uv run python -m mcp_pdfco.server

# Using the Makefile
make run
```

### Production Mode (Docker)

```bash
# Build the Docker image
docker build -t mcp-pdfco .

# Run with Docker
docker run -e PDFCO_API_KEY=your_key -p 8000:8000 mcp-pdfco

# Run with Docker Compose
docker-compose up
```

### HTTP Transport

The server supports HTTP transport with a health check endpoint:

```bash
# Start with uvicorn
uvicorn mcp_pdfco.server:app --host 0.0.0.0 --port 8000

# Check health
curl http://localhost:8000/health
```

## Usage Examples

### Extract Text from PDF

```python
result = await pdf_to_text(
    url="https://example.com/document.pdf",
    pages="1-5"
)
print(result.text)
```

### Merge Multiple PDFs

```python
result = await pdf_merge(
    urls=[
        "https://example.com/doc1.pdf",
        "https://example.com/doc2.pdf"
    ],
    name="merged_document.pdf"
)
print(f"Merged PDF: {result.url}")
```

### Convert HTML to PDF

```python
result = await html_to_pdf(
    html="<h1>Hello World</h1><p>This is a PDF</p>",
    name="hello.pdf",
    page_size="A4",
    orientation="Portrait"
)
print(f"Generated PDF: {result.url}")
```

### Add Watermark

```python
result = await pdf_add_watermark(
    url="https://example.com/document.pdf",
    text="CONFIDENTIAL",
    x=200,
    y=400,
    font_size=48,
    color="FF0000",
    opacity=0.3,
    pages="0-",  # Apply to all pages
    name="watermarked_document.pdf"
)
print(f"Watermarked PDF: {result.url}")
```

### Generate QR Code

```python
result = await barcode_generate(
    value="https://example.com",
    barcode_type="QRCode",
    format="png"
)
print(f"QR Code: {result.url}")
```

### OCR a Scanned PDF

```python
result = await ocr_pdf(
    url="https://example.com/scanned.pdf",
    pages="1-10",
    lang="eng"
)
print(f"OCR'd PDF: {result.url}")
print(f"Extracted text: {result.text}")
```

## Development

### Quick Start

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev-install   # Install with dev dependencies
make format        # Format code with ruff
make lint          # Lint code with ruff
make typecheck     # Type check with mypy
make test          # Run tests with pytest
make test-cov      # Run tests with coverage
make check         # Run all checks (lint + typecheck + test)
make clean         # Clean up artifacts
```

### Project Structure

```
.
├── src/
│   └── mcp_pdfco/
│       ├── __init__.py
│       ├── server.py          # FastMCP server with tool definitions
│       ├── api_client.py      # Async PDF.co API client
│       └── api_models.py      # Pydantic models for type safety
├── tests/
│   ├── __init__.py
│   ├── test_server.py         # Server tool tests
│   └── test_api_client.py     # API client tests
├── pyproject.toml             # Project configuration
├── Makefile                   # Development commands
├── Dockerfile                 # Container deployment
└── README.md                  # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mcp_pdfco --cov-report=term-missing

# Run specific test file
pytest tests/test_server.py -v
```

### Code Quality

This project uses:
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker (strict mode)
- **pytest**: Testing framework with async support

All code must pass:
```bash
make check  # Runs lint + typecheck + test
```

## Architecture

This server follows S-Tier MCP architecture principles:

1. **Separation of Concerns**
   - `api_client.py`: HTTP communication layer
   - `api_models.py`: Data models and type definitions
   - `server.py`: MCP tool definitions and routing

2. **Type Safety**
   - Full type hints on all functions
   - Pydantic models for API responses
   - Mypy strict mode compliance

3. **Async All the Way**
   - aiohttp for HTTP requests
   - Async/await throughout
   - Context managers for resource cleanup

4. **Error Handling**
   - Custom `PDFcoAPIError` exception
   - Context logging via `ctx.error()` and `ctx.warning()`
   - Graceful error messages

5. **Production Ready**
   - Docker support
   - Health check endpoint
   - Environment-based configuration
   - Comprehensive logging

## Requirements

- Python 3.13+
- aiohttp >= 3.12.15
- fastmcp >= 2.14.0
- pydantic >= 2.0.0

## API Documentation

For detailed API documentation, visit [PDF.co API Documentation](https://apidocs.pdf.co/).

### Supported Input Formats

- **PDF**: URL or base64 encoded
- **Images**: PNG, JPG, GIF, BMP, TIFF
- **HTML**: Raw HTML string or URL

### Supported Output Formats

- **PDF**: High-quality PDF generation
- **Text**: Plain text extraction
- **JSON**: Structured data extraction
- **HTML**: Formatted HTML output
- **CSV**: Table data extraction
- **Images**: PNG, JPG, SVG for barcodes

### Rate Limits

PDF.co has rate limits based on your subscription plan. Free plans include:
- 100 API calls per month
- 10 API calls per minute

Check your [dashboard](https://app.pdf.co/dashboard) for current usage.

## Troubleshooting

### Common Issues

**Issue**: `PDFCO_API_KEY is not set` warning

**Solution**: Set the environment variable:
```bash
export PDFCO_API_KEY=your_key_here
```

**Issue**: `Network error` or timeout

**Solution**: Check your internet connection and increase timeout:
```python
client = PDFcoClient(timeout=180.0)  # 3 minutes
```

**Issue**: `API Error 401: Unauthorized`

**Solution**: Verify your API key is valid at https://app.pdf.co/dashboard

**Issue**: Docker container won't start

**Solution**: Ensure the API key is passed correctly:
```bash
docker run -e PDFCO_API_KEY=your_key_here -p 8000:8000 mcp-pdfco
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make check`
5. Submit a pull request

Issue Tracker: [GitHub Issues](https://github.com/your-org/mcp-pdfco/issues)

## License

MIT

## Links

Part of the [NimbleTools Registry](https://github.com/nimbletoolsinc/mcp-registry) - an open source collection of production-ready MCP servers. For enterprise deployment, check out [NimbleBrain](https://www.nimblebrain.ai).

### API Documentation

- [PDF.co Documentation](https://apidocs.pdf.co/)
- [PDF Operations](https://apidocs.pdf.co/02-pdf-to-text)
- [Conversion APIs](https://apidocs.pdf.co/07-html-to-pdf)
- [OCR API](https://apidocs.pdf.co/12-pdf-ocr)
- [Barcode API](https://apidocs.pdf.co/24-barcode-generate)

### Support

- [Help Center](https://pdf.co/support)
- [API Documentation](https://apidocs.pdf.co/)
- [Contact Support](https://pdf.co/contact)
- [Status Page](https://status.pdf.co/)
- Built with [FastMCP](https://github.com/jlowin/fastmcp)
