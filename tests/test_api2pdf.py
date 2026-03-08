import pytest
import requests

import api2pdf
from api2pdf import Api2Pdf
from api2pdf.api2pdf import Api2PdfResponse


class MockResponse(object):
    def __init__(
        self,
        status_code=200,
        json_data=None,
        text="",
        content=None,
        headers=None,
    ):
        self.status_code = status_code
        self._json_data = json_data
        if json_data is not None and not text and content is None:
            text = str(json_data)
            content = text.encode("utf-8")
        self._text = text
        self.content = content if content is not None else text.encode("utf-8")
        self.headers = headers or {}

    @property
    def ok(self):
        return self.status_code < 400

    @property
    def text(self):
        return self._text

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON payload")
        return self._json_data

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError(self.text or "request failed")


class DummySession(object):
    def __init__(self, responses=None, get_responses=None):
        self.responses = list(responses or [])
        self.get_responses = list(get_responses or [])
        self.calls = []
        self.get_calls = []

    def request(self, method, url, json=None, params=None, headers=None, timeout=None):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "json": json,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self.responses.pop(0)

    def get(self, url, headers=None, timeout=None):
        self.get_calls.append(
            {
                "url": url,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self.get_responses.pop(0)


def test_package_exports_are_explicit():
    assert api2pdf.Api2Pdf is Api2Pdf
    assert api2pdf.DEFAULT_BASE_URL == "https://v2.api2pdf.com"
    assert api2pdf.__version__ == "2.2.0"


def test_chrome_markdown_to_pdf_builds_expected_request():
    session = DummySession(
        responses=[
            MockResponse(
                json_data={
                    "Success": True,
                    "FileUrl": "https://files.example.com/out.pdf",
                },
                headers={"Content-Type": "application/json"},
            )
        ]
    )
    client = Api2Pdf("api-key", tag="release", session=session)

    response = client.Chrome.markdown_to_pdf(
        "# Hello",
        file_name="doc.pdf",
        output_binary=True,
        DisplayHeaderFooter=True,
    )

    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://v2.api2pdf.com/chrome/pdf/markdown"
    assert call["params"] == {"outputBinary": "true"}
    assert call["headers"]["Authorization"] == "api-key"
    assert call["headers"]["Tag"] == "release"
    assert call["json"]["markdown"] == "# Hello"
    assert call["json"]["fileName"] == "doc.pdf"
    assert call["json"]["options"] == {"DisplayHeaderFooter": True}
    assert response.result["Success"] is True


def test_get_url_shortcut_uses_get_endpoint():
    session = DummySession(
        responses=[
            MockResponse(
                json_data={
                    "Success": True,
                    "FileUrl": "https://files.example.com/url.pdf",
                },
                headers={"Content-Type": "application/json"},
            )
        ]
    )
    client = Api2Pdf("api-key", session=session)

    client.Chrome.url_to_pdf("https://www.api2pdf.com", use_get=True, output_binary=True)

    call = session.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == "https://v2.api2pdf.com/chrome/pdf/url"
    assert call["json"] is None
    assert call["params"] == {"url": "https://www.api2pdf.com", "outputBinary": "true"}


@pytest.mark.parametrize(
    ("method_name", "expected_url", "payload_key", "payload_value"),
    [
        ("convert_to_markdown", "https://v2.api2pdf.com/markitdown", "url", "https://example.com/file.docx"),
        ("pdf_to_json", "https://v2.api2pdf.com/opendataloader/json", "url", "https://example.com/file.pdf"),
        ("pdf_to_markdown", "https://v2.api2pdf.com/opendataloader/markdown", "url", "https://example.com/file.pdf"),
        ("pdf_to_html", "https://v2.api2pdf.com/opendataloader/html", "url", "https://example.com/file.pdf"),
    ],
)
def test_new_document_services_route_to_expected_endpoints(
    method_name, expected_url, payload_key, payload_value
):
    session = DummySession(
        responses=[
            MockResponse(
                json_data={"Success": True, "FileUrl": "https://files.example.com/out"},
                headers={"Content-Type": "application/json"},
            )
        ]
    )
    client = Api2Pdf("api-key", session=session)

    if method_name == "convert_to_markdown":
        getattr(client.Markitdown, method_name)(payload_value, output_binary=False)
    else:
        getattr(client.OpenDataLoader, method_name)(payload_value, output_binary=False)

    call = session.calls[0]
    assert call["url"] == expected_url
    assert call["json"][payload_key] == payload_value
    assert call["params"] == {"outputBinary": "false"}


def test_zip_and_zebra_endpoints_use_current_swagger_routes():
    session = DummySession(
        responses=[
            MockResponse(text="zip-bytes", headers={"Content-Type": "application/zip"}),
            MockResponse(text="png-bytes", headers={"Content-Type": "image/png"}),
        ]
    )
    client = Api2Pdf("api-key", session=session)

    zip_response = client.Zip.generate_zip(
        [{"url": "https://example.com/report.pdf", "fileName": "docs/report.pdf"}]
    )
    zebra_response = client.Zebra.generate_barcode(
        "QR_CODE",
        "https://www.api2pdf.com",
        width=300,
        height=300,
    )

    zip_call = session.calls[0]
    zebra_call = session.calls[1]
    assert zip_call["url"] == "https://v2.api2pdf.com/zip"
    assert zip_call["params"] == {"outputBinary": "true"}
    assert zip_call["json"]["files"][0]["fileName"] == "docs/report.pdf"
    assert zebra_call["method"] == "GET"
    assert zebra_call["url"] == "https://v2.api2pdf.com/zebra"
    assert zebra_call["params"]["format"] == "QR_CODE"
    assert zebra_call["params"]["showlabel"] == "false"
    assert zip_response.is_binary is True
    assert zebra_response.is_binary is True


def test_libreoffice_html_to_docx_accepts_html_or_url():
    session = DummySession(
        responses=[
            MockResponse(
                json_data={"Success": True, "FileUrl": "https://files.example.com/doc.docx"},
                headers={"Content-Type": "application/json"},
            ),
            MockResponse(
                json_data={"Success": True, "FileUrl": "https://files.example.com/doc.docx"},
                headers={"Content-Type": "application/json"},
            ),
        ]
    )
    client = Api2Pdf("api-key", session=session)

    client.LibreOffice.html_to_docx(html="<p>Hello</p>")
    client.LibreOffice.html_to_docx("https://example.com/source.html")

    first_call = session.calls[0]
    second_call = session.calls[1]
    assert first_call["json"]["html"] == "<p>Hello</p>"
    assert "url" not in first_call["json"]
    assert second_call["json"]["url"] == "https://example.com/source.html"


def test_response_downloads_file_url_when_json_response_points_to_file():
    session = DummySession(
        get_responses=[
            MockResponse(
                content=b"%PDF-1.7",
                headers={"Content-Type": "application/pdf"},
            )
        ]
    )
    response = Api2PdfResponse(
        {
            "headers": {"Authorization": "api-key"},
            "endpoint": "https://v2.api2pdf.com/chrome/pdf/html",
            "payload": {"html": "<p>Hello</p>"},
            "query_params": {"outputBinary": "false"},
        },
        MockResponse(
            json_data={
                "Success": True,
                "FileUrl": "https://files.example.com/out.pdf",
            },
            headers={"Content-Type": "application/json"},
        ),
        session,
    )

    file_bytes = response.get_file_bytes()

    assert file_bytes == b"%PDF-1.7"
    assert session.get_calls[0]["url"] == "https://files.example.com/out.pdf"


def test_binary_responses_are_returned_directly():
    session = DummySession()
    response = Api2PdfResponse(
        {
            "headers": {"Authorization": "api-key"},
            "endpoint": "https://v2.api2pdf.com/zip",
            "payload": {"files": []},
            "query_params": {"outputBinary": "true"},
        },
        MockResponse(
            text="zip-bytes",
            headers={"Content-Type": "application/zip"},
        ),
        session,
    )

    assert response.is_binary is True
    assert response.get_file_bytes() == b"zip-bytes"
    assert response.result is None


def test_utilities_support_status_balance_and_delete():
    session = DummySession(
        responses=[
            MockResponse(
                json_data={"Success": True},
                headers={"Content-Type": "application/json"},
            )
        ],
        get_responses=[
            MockResponse(text="up", headers={"Content-Type": "text/plain"}),
            MockResponse(text="12.34", headers={"Content-Type": "text/plain"}),
        ],
    )
    client = Api2Pdf("api-key", session=session)

    assert client.status() == "up"
    assert client.balance() == "12.34"

    delete_response = client.delete("response-id")

    delete_call = session.calls[0]
    assert delete_call["method"] == "DELETE"
    assert delete_call["url"] == "https://v2.api2pdf.com/file/response-id"
    assert delete_response.result["Success"] is True
