import json
from pathlib import Path

import requests


DEFAULT_BASE_URL = "https://v2.api2pdf.com"
DEFAULT_TIMEOUT = 120
DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/39.0.2171.95 Safari/537.36"
    )
}


def _coalesce_result_value(result, *keys):
    if not isinstance(result, dict):
        return None

    for key in keys:
        if key in result:
            return result[key]

    lowered = {str(existing_key).lower(): value for existing_key, value in result.items()}
    for key in keys:
        lowered_key = key.lower()
        if lowered_key in lowered:
            return lowered[lowered_key]

    return None


class Api2PdfError(Exception):
    pass


class Api2PdfResponse(object):
    def __init__(self, request_info, response, session):
        self.headers = request_info["headers"]
        self.endpoint = request_info["endpoint"]
        self.payload_as_json = request_info["payload"]
        self.query_params = request_info["query_params"]
        self.status_code = response.status_code
        self.response_headers = dict(response.headers)
        self._response = response
        self._session = session
        self._result = None
        self._binary_content = None
        self._parse_response()

    def _parse_response(self):
        if not self._response.content:
            self._result = {}
            return

        try:
            self._result = self._response.json()
        except ValueError:
            if self._response.ok:
                self._binary_content = self._response.content
                return

            self._result = {
                "Success": False,
                "Error": self._response.text or "Api2Pdf request failed.",
                "StatusCode": self._response.status_code,
            }

    @property
    def request(self):
        return {
            "headers": self.headers,
            "endpoint": self.endpoint,
            "payload": self.payload_as_json,
            "query_params": self.query_params,
        }

    @property
    def result(self):
        return self._result

    @property
    def is_binary(self):
        return self._binary_content is not None

    def get_file_bytes(self):
        if self._binary_content is not None:
            return self._binary_content

        file_url = _coalesce_result_value(self.result, "FileUrl", "fileUrl")
        success = _coalesce_result_value(self.result, "Success", "success")
        error = _coalesce_result_value(self.result, "Error", "error")

        if success and file_url:
            downloaded_file = self._session.get(file_url, headers=DOWNLOAD_HEADERS)
            downloaded_file.raise_for_status()
            return downloaded_file.content

        raise FileNotFoundError("File never generated {0}".format(error or ""))

    def download_file(self):
        return self.get_file_bytes()

    def save_file(self, path):
        file_path = Path(path)
        file_path.write_bytes(self.get_file_bytes())
        return file_path

    def __str__(self):
        response_data = self.result
        if self.is_binary:
            response_data = {"binary_bytes": len(self._binary_content)}

        return """
---- API2PDF REQUEST ----
- Headers: {0}
- Endpoint: {1}
- Query Params: {2}
- Payload:
{3}
---- API2PDF RESPONSE ----
{4}
""".format(
            self.headers,
            self.endpoint,
            self.query_params,
            self.payload_as_json,
            response_data,
        )


class _Api2PdfService(object):
    def __init__(
        self,
        api_key,
        base_url=DEFAULT_BASE_URL,
        tag="",
        timeout=DEFAULT_TIMEOUT,
        session=None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.tag = tag
        self.timeout = timeout
        self._session = session or requests.Session()

    @property
    def request_header(self):
        header = {
            "Authorization": self.api_key,
            "Accept": "application/json, application/octet-stream",
        }
        if self.tag:
            header["Tag"] = self.tag
        return header

    def _build_base_payload(
        self,
        inline=True,
        file_name=None,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = {}
        if inline is not None:
            payload["inline"] = inline
        if file_name is not None:
            payload["fileName"] = file_name
        if inline_pdf is not None:
            payload["inlinePdf"] = inline_pdf
        if use_custom_storage is not None:
            payload["useCustomStorage"] = use_custom_storage
        if storage is not None:
            payload["storage"] = storage
        if extra_http_headers is not None:
            payload["extraHTTPHeaders"] = extra_http_headers
        return payload

    def _add_options(self, payload, options=None):
        if options:
            payload["options"] = options
        return payload

    def _normalize_query_params(self, params):
        normalized = {}
        for key, value in (params or {}).items():
            if value is None:
                continue
            if isinstance(value, bool):
                normalized[key] = str(value).lower()
            else:
                normalized[key] = value
        return normalized

    def _make_request(self, method, endpoint, payload=None, query_params=None):
        url = "{0}{1}".format(self.base_url, endpoint)
        query_params = self._normalize_query_params(query_params)
        response = self._session.request(
            method,
            url,
            json=payload,
            params=query_params or None,
            headers=self.request_header,
            timeout=self.timeout,
        )
        request_info = {
            "headers": dict(self.request_header),
            "endpoint": url,
            "payload": payload,
            "query_params": query_params,
        }
        return Api2PdfResponse(request_info, response, self._session)

    def _make_text_request(self, endpoint):
        url = "{0}{1}".format(self.base_url, endpoint)
        response = self._session.get(
            url,
            headers=self.request_header,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text.strip()


class Api2Pdf_WkHtml(_Api2PdfService):
    def html_to_pdf(
        self,
        html,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        enable_toc=None,
        toc_options=None,
        **options
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["html"] = html
        if enable_toc is not None:
            payload["enableToc"] = enable_toc
        if toc_options is not None:
            payload["tocOptions"] = toc_options
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/wkhtml/pdf/html",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def url_to_pdf(
        self,
        url,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        enable_toc=None,
        toc_options=None,
        use_get=False,
        **options
    ):
        if use_get:
            return self._make_request(
                "GET",
                "/wkhtml/pdf/url",
                query_params={"url": url, "outputBinary": output_binary},
            )

        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["url"] = url
        if enable_toc is not None:
            payload["enableToc"] = enable_toc
        if toc_options is not None:
            payload["tocOptions"] = toc_options
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/wkhtml/pdf/url",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_Chrome(_Api2PdfService):
    def html_to_pdf(
        self,
        html,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        **options
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["html"] = html
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/pdf/html",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def markdown_to_pdf(
        self,
        markdown,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        **options
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["markdown"] = markdown
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/pdf/markdown",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def url_to_pdf(
        self,
        url,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
        use_get=False,
        **options
    ):
        if use_get:
            return self._make_request(
                "GET",
                "/chrome/pdf/url",
                query_params={"url": url, "outputBinary": output_binary},
            )

        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/pdf/url",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def html_to_image(
        self,
        html,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        **options
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["html"] = html
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/image/html",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def markdown_to_image(
        self,
        markdown,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        **options
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
        )
        payload["markdown"] = markdown
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/image/markdown",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def url_to_image(
        self,
        url,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
        use_get=False,
        **options
    ):
        if use_get:
            return self._make_request(
                "GET",
                "/chrome/image/url",
                query_params={"url": url, "outputBinary": output_binary},
            )

        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        self._add_options(payload, options)
        return self._make_request(
            "POST",
            "/chrome/image/url",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_LibreOffice(_Api2PdfService):
    def any_to_pdf(
        self,
        url,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/libreoffice/any-to-pdf",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def thumbnail(
        self,
        url,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/libreoffice/thumbnail",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def html_to_docx(
        self,
        value=None,
        *,
        url=None,
        html=None,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        if html is None and url is None and value is not None:
            url = value
        if html is not None:
            payload["html"] = html
        if url is not None:
            payload["url"] = url
        return self._make_request(
            "POST",
            "/libreoffice/html-to-docx",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def html_to_xlsx(
        self,
        value=None,
        *,
        url=None,
        html=None,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        if html is None and url is None and value is not None:
            url = value
        if html is not None:
            payload["html"] = html
        if url is not None:
            payload["url"] = url
        return self._make_request(
            "POST",
            "/libreoffice/html-to-xlsx",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_Markitdown(_Api2PdfService):
    def convert_to_markdown(
        self,
        url,
        file_name=None,
        output_binary=False,
        inline=None,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/markitdown",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_OpenDataLoader(_Api2PdfService):
    def pdf_to_json(
        self,
        url,
        file_name=None,
        output_binary=False,
        inline=None,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/opendataloader/json",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def pdf_to_markdown(
        self,
        url,
        file_name=None,
        output_binary=False,
        inline=None,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/opendataloader/markdown",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def pdf_to_html(
        self,
        url,
        file_name=None,
        output_binary=False,
        inline=None,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        return self._make_request(
            "POST",
            "/opendataloader/html",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_PdfSharp(_Api2PdfService):
    def merge(
        self,
        urls,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["urls"] = urls
        return self._make_request(
            "POST",
            "/pdfsharp/merge",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def add_password(
        self,
        url,
        user_password,
        owner_password=None,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        payload["userPassword"] = user_password
        if owner_password is not None:
            payload["ownerPassword"] = owner_password
        return self._make_request(
            "POST",
            "/pdfsharp/password",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )

    def extract_pages(
        self,
        url,
        start=0,
        end=0,
        inline=True,
        file_name=None,
        output_binary=False,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["url"] = url
        payload["start"] = start
        payload["end"] = end
        return self._make_request(
            "POST",
            "/pdfsharp/extract-pages",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_Zip(_Api2PdfService):
    def generate_zip(
        self,
        files,
        file_name=None,
        inline=True,
        output_binary=True,
        inline_pdf=None,
        use_custom_storage=None,
        storage=None,
        extra_http_headers=None,
    ):
        payload = self._build_base_payload(
            inline=inline,
            file_name=file_name,
            inline_pdf=inline_pdf,
            use_custom_storage=use_custom_storage,
            storage=storage,
            extra_http_headers=extra_http_headers,
        )
        payload["files"] = files
        return self._make_request(
            "POST",
            "/zip",
            payload=payload,
            query_params={"outputBinary": output_binary},
        )


class Api2Pdf_Zebra(_Api2PdfService):
    def generate_barcode(
        self,
        format,
        value,
        width=None,
        height=None,
        show_label=False,
        output_binary=True,
    ):
        return self._make_request(
            "GET",
            "/zebra",
            query_params={
                "format": format,
                "value": value,
                "width": width,
                "height": height,
                "showlabel": show_label,
                "outputBinary": output_binary,
            },
        )


class Api2Pdf_Utilities(_Api2PdfService):
    def status(self):
        return self._make_text_request("/status")

    def balance(self):
        return self._make_text_request("/balance")

    def delete(self, response_id):
        return self._make_request("DELETE", "/file/{0}".format(response_id))


class Api2Pdf(_Api2PdfService):
    def __init__(
        self,
        api_key,
        base_url=DEFAULT_BASE_URL,
        tag="",
        timeout=DEFAULT_TIMEOUT,
        session=None,
    ):
        super(Api2Pdf, self).__init__(
            api_key=api_key,
            base_url=base_url,
            tag=tag,
            timeout=timeout,
            session=session,
        )
        self._wkhtml = Api2Pdf_WkHtml(api_key, self.base_url, tag, timeout, self._session)
        self._chrome = Api2Pdf_Chrome(api_key, self.base_url, tag, timeout, self._session)
        self._libreoffice = Api2Pdf_LibreOffice(
            api_key, self.base_url, tag, timeout, self._session
        )
        self._markitdown = Api2Pdf_Markitdown(
            api_key, self.base_url, tag, timeout, self._session
        )
        self._opendataloader = Api2Pdf_OpenDataLoader(
            api_key, self.base_url, tag, timeout, self._session
        )
        self._pdfsharp = Api2Pdf_PdfSharp(api_key, self.base_url, tag, timeout, self._session)
        self._zip = Api2Pdf_Zip(api_key, self.base_url, tag, timeout, self._session)
        self._zebra = Api2Pdf_Zebra(api_key, self.base_url, tag, timeout, self._session)
        self._utilities = Api2Pdf_Utilities(
            api_key, self.base_url, tag, timeout, self._session
        )

    @property
    def WkHtml(self):
        return self._wkhtml

    @property
    def Chrome(self):
        return self._chrome

    @property
    def LibreOffice(self):
        return self._libreoffice

    @property
    def Markitdown(self):
        return self._markitdown

    @property
    def OpenDataLoader(self):
        return self._opendataloader

    @property
    def PdfSharp(self):
        return self._pdfsharp

    @property
    def Zip(self):
        return self._zip

    @property
    def Zebra(self):
        return self._zebra

    @property
    def Utilities(self):
        return self._utilities

    def status(self):
        return self.Utilities.status()

    def balance(self):
        return self.Utilities.balance()

    def delete(self, response_id):
        return self.Utilities.delete(response_id)
