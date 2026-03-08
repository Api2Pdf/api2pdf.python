# api2pdf.python

Python bindings for the [Api2Pdf REST API](https://v2.api2pdf.com).

Api2Pdf.com is a document generation and file conversion API for Python applications. It supports HTML to PDF, URL to PDF, HTML to image, URL to image, Office document conversion, markdown conversion, structured PDF extraction, zip generation, barcode and QR code generation, PDF page extraction, PDF password protection, and thumbnails or previews for PDF, office, and email files.

The package keeps a simple Pythonic client shape with service groups like `client.Chrome`, `client.WkHtml`, and `client.PdfSharp`.

## Installation

Install from PyPI:

```bash
pip install api2pdf
```

## Quick Start

Create an account at [portal.api2pdf.com](https://portal.api2pdf.com/register) to get your API key.

```python
from api2pdf import Api2Pdf

client = Api2Pdf("YOUR-API-KEY")

result = client.Chrome.html_to_pdf("<html><body><h1>Hello, world!</h1></body></html>")

if result.result["Success"]:
    print(result.result["FileUrl"])
else:
    print(result.result["Error"])
```

## Custom Domains

The default client base URL is `https://v2.api2pdf.com`.

To send requests to a custom Api2Pdf domain:

```python
from api2pdf import Api2Pdf

client = Api2Pdf("YOUR-API-KEY", base_url="https://your-custom-domain.api2pdf.com")
```

You can also attach a tag header to all requests:

```python
client = Api2Pdf("YOUR-API-KEY", tag="billing-batch")
```

## Understanding Responses

Most conversion methods return an `Api2PdfResponse`.

```python
{
    "FileUrl": "https://link-to-file-available-for-24-hours",
    "MbOut": 0.08830547332763672,
    "Cost": 0.00017251586914062501,
    "Seconds": 2,
    "Success": True,
    "Error": None,
    "ResponseId": "6e46637a-650d-46d5-af0b-3d7831baccbb",
}
```

Important members:

- `result`: Parsed JSON response when the API returns standard JSON.
- `is_binary`: `True` when `output_binary=True` returns file bytes directly.
- `get_file_bytes()`: Return bytes from a binary response or download them from `FileUrl`.
- `download_file()`: Backward-compatible alias for `get_file_bytes()`.
- `save_file(path)`: Save the generated file to disk.
- `request`: Request metadata useful for debugging.

For debugging:

```python
response = client.Chrome.html_to_pdf("<p>Hello, world!</p>")
print(response)
```

## Common Request Features

Most conversion methods support some or all of these keyword arguments:

- `file_name`: Set the output file name.
- `inline`: Control browser inline display behavior.
- `use_custom_storage` and `storage`: Send output directly to your own storage target.
- `extra_http_headers`: Forward custom headers when Api2Pdf fetches a source URL.
- `output_binary`: Request raw file bytes instead of the standard JSON payload when the endpoint supports it.
- `use_get=True`: Use the simple GET-style URL endpoints for selected URL conversions.

Example custom storage configuration:

```python
request_storage = {
    "method": "PUT",
    "url": "https://your-presigned-upload-url",
}

result = client.Chrome.html_to_pdf(
    "<p>Hello World</p>",
    use_custom_storage=True,
    storage=request_storage,
)
```

## Chrome

### HTML or URL to PDF

```python
html_pdf = client.Chrome.html_to_pdf(
    "<p>Hello World</p>",
    DisplayHeaderFooter=True,
    HeaderTemplate="<div style='font-size:12px;'>Header</div>",
    FooterTemplate="<div style='font-size:12px;'>Footer</div>",
    Landscape=True,
    PreferCSSPageSize=True,
)

url_pdf = client.Chrome.url_to_pdf(
    "https://www.api2pdf.com",
    extra_http_headers={"Authorization": "Bearer token-for-the-source-site"},
    PuppeteerWaitForMethod="WaitForNavigation",
    PuppeteerWaitForValue="Load",
)
```

For the simple GET route:

```python
result = client.Chrome.url_to_pdf("https://www.api2pdf.com", use_get=True)
```

### Markdown to PDF

```python
result = client.Chrome.markdown_to_pdf("# Invoice\n\nGenerated from markdown.")
```

### HTML, URL, or Markdown to Image

```python
html_image = client.Chrome.html_to_image(
    "<p>Hello image</p>",
    FullPage=True,
    ViewPortOptions={"Width": 1440, "Height": 900},
)

url_image = client.Chrome.url_to_image("https://www.api2pdf.com", use_get=True)

markdown_image = client.Chrome.markdown_to_image("# Screenshot\n\nGenerated from markdown.")
```

## Wkhtmltopdf

```python
html_pdf = client.WkHtml.html_to_pdf(
    "<p>Hello World</p>",
    orientation="landscape",
    pageSize="Letter",
)

url_pdf = client.WkHtml.url_to_pdf(
    "https://www.api2pdf.com",
    enable_toc=True,
    toc_options={"disableDottedLines": "true"},
)
```

For the simple GET route:

```python
result = client.WkHtml.url_to_pdf("https://www.api2pdf.com", use_get=True)
```

## LibreOffice

Use LibreOffice endpoints for file and Office conversions.

Convert a file URL to PDF:

```python
result = client.LibreOffice.any_to_pdf(
    "https://www.api2pdf.com/wp-content/themes/api2pdf/assets/samples/sample-word-doc.docx"
)
```

Generate a thumbnail:

```python
result = client.LibreOffice.thumbnail(
    "https://www.api2pdf.com/wp-content/themes/api2pdf/assets/samples/sample-word-doc.docx"
)
```

Convert HTML or a URL to DOCX or XLSX:

```python
docx = client.LibreOffice.html_to_docx(
    html="<html><body><h1>Hello Word</h1></body></html>"
)

xlsx = client.LibreOffice.html_to_xlsx(
    url="https://www.api2pdf.com/wp-content/uploads/2021/01/sampleTables.html"
)
```

## Markitdown

Convert a file URL to markdown:

```python
result = client.Markitdown.convert_to_markdown("https://example.com/sample.docx")
```

## OpenDataLoader

Extract structured content from a PDF URL:

```python
json_result = client.OpenDataLoader.pdf_to_json("https://example.com/sample.pdf")

markdown_result = client.OpenDataLoader.pdf_to_markdown("https://example.com/sample.pdf")

html_result = client.OpenDataLoader.pdf_to_html("https://example.com/sample.pdf")
```

## PdfSharp

Merge PDFs:

```python
result = client.PdfSharp.merge(
    [
        "https://LINK-TO-PDF-1",
        "https://LINK-TO-PDF-2",
    ]
)
```

Set a password:

```python
result = client.PdfSharp.add_password(
    "https://LINK-TO-PDF",
    user_password="password",
    owner_password="owner-password",
)
```

Extract a page range:

```python
result = client.PdfSharp.extract_pages(
    "https://LINK-TO-PDF",
    start=0,
    end=2,
)
```

## Zip

Create a zip from multiple files:

```python
result = client.Zip.generate_zip(
    [
        {"url": "https://example.com/report.pdf", "fileName": "docs/report.pdf"},
        {"url": "https://example.com/image.png", "fileName": "images/image.png"},
    ],
    output_binary=True,
)

zip_bytes = result.get_file_bytes()
```

## Zebra

Generate a barcode or QR code:

```python
result = client.Zebra.generate_barcode(
    "QR_CODE",
    "https://www.api2pdf.com",
    width=300,
    height=300,
    show_label=False,
)
```

## Utilities

Delete a generated file:

```python
result = client.Chrome.html_to_pdf("<p>Hello World</p>")
client.Utilities.delete(result.result["ResponseId"])
```

Check API status or remaining balance:

```python
status = client.Utilities.status()
balance = client.Utilities.balance()
```

Top-level shortcuts are also available:

```python
client.delete(result.result["ResponseId"])
print(client.status())
print(client.balance())
```

## Working With Files

Save a generated file to disk:

```python
result = client.Chrome.html_to_pdf("<p>Hello World</p>")
result.save_file("path-to-local-file.pdf")
```

Get bytes directly:

```python
result = client.Chrome.html_to_pdf(
    "<p>Hello World</p>",
    output_binary=True,
)

file_bytes = result.get_file_bytes()
```

## Development

Install the project in editable mode with test dependencies:

```bash
python3 -m venv .venv
./.venv/bin/pip install -e .[test]
```

Run the test suite:

```bash
./.venv/bin/python -m pytest
```

## Resources

- [Api2Pdf documentation](https://v2.api2pdf.com)
- [Api2Pdf FAQ](https://www.api2pdf.com/faq)
