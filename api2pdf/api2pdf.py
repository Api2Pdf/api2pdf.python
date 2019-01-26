import requests
import json

API2PDF_BASE_ENDPOINT = 'https://v2018.api2pdf.com'
API2PDF_MERGE_ENDPOINT = API2PDF_BASE_ENDPOINT + '/merge'
API2PDF_WKHTMLTOPDF_HTML = API2PDF_BASE_ENDPOINT + '/wkhtmltopdf/html'
API2PDF_WKHTMLTOPDF_URL = API2PDF_BASE_ENDPOINT + '/wkhtmltopdf/url'
API2PDF_CHROME_HTML = API2PDF_BASE_ENDPOINT + '/chrome/html'
API2PDF_CHROME_URL = API2PDF_BASE_ENDPOINT + '/chrome/url'
API2PDF_LIBREOFFICE_CONVERT = API2PDF_BASE_ENDPOINT + '/libreoffice/convert'
API2PDF_DELETE_PDF = API2PDF_BASE_ENDPOINT + '/pdf/{response_id}'

class Api2Pdf(object):
    def __init__(self, api_key, tag=''):
        self.api_key = api_key
        self.tag = tag

    @property
    def WkHtmlToPdf(self):
        return Api2Pdf_WkHtmlToPdf(self.api_key)

    @property
    def HeadlessChrome(self):
        return Api2Pdf_HeadlessChromeToPdf(self.api_key)

    @property
    def LibreOffice(self):
        return Api2Pdf_LibreOffice(self.api_key)

    def merge(self, list_of_urls, inline_pdf=False, file_name=None):
        payload = {
            'urls': list_of_urls,
            'inlinePdf': inline_pdf
        }
        if file_name != None:
            payload['fileName'] = file_name
        return self._make_request(API2PDF_MERGE_ENDPOINT, payload)

    def delete(self, response_id):
        headers = self.request_header
        endpoint = API2PDF_DELETE_PDF.format(response_id=response_id)
        response = requests.delete(endpoint, headers=headers)
        return Api2PdfResponse(headers, endpoint, '', response)

    def _make_html_payload(self, html, inline_pdf=False, file_name=None, **options):
        payload = {
            'html': html,
            'inlinePdf': inline_pdf
        }
        if file_name != None:
            payload['fileName'] = file_name

        if options != None:
            payload['options'] = options
        return payload

    def _make_url_payload(self, url, inline_pdf=False, file_name=None, **options):
        payload = {
            'url': url,
            'inlinePdf': inline_pdf
        }
        if file_name != None:
            payload['fileName'] = file_name
        if options != None:
            payload['options'] = options
        return payload

    def _make_request(self, endpoint, payload):
        headers = self.request_header
        payload_as_json = json.dumps(payload)
        response = requests.post(endpoint, data=payload_as_json, headers=headers)
        return Api2PdfResponse(headers, endpoint, payload, response)

    @property
    def request_header(self):
        header = {}
        header['Authorization'] = self.api_key
        if self.tag:
            header['Tag'] = self.tag
        return header

class Api2Pdf_WkHtmlToPdf(Api2Pdf):
    def convert_from_html(self, html, inline_pdf=False, file_name=None, **options):
        payload = self._make_html_payload(html, inline_pdf=inline_pdf, file_name=file_name, **options)
        return self._make_request(API2PDF_WKHTMLTOPDF_HTML, payload)
    
    def convert_from_url(self, url, inline_pdf=False, file_name=None, **options):
        payload = self._make_url_payload(url, inline_pdf=inline_pdf, file_name=file_name, **options)
        return self._make_request(API2PDF_WKHTMLTOPDF_URL, payload)

class Api2Pdf_HeadlessChromeToPdf(Api2Pdf):
    def convert_from_html(self, html, inline_pdf=False, file_name=None, **options):
        payload = self._make_html_payload(html, inline_pdf=inline_pdf, file_name=file_name, **options)
        return self._make_request(API2PDF_CHROME_HTML, payload)
    
    def convert_from_url(self, url, inline_pdf=False, file_name=None, **options):
        payload = self._make_url_payload(url, inline_pdf=inline_pdf, file_name=file_name, **options)
        return self._make_request(API2PDF_CHROME_URL, payload)

class Api2Pdf_LibreOffice(Api2Pdf):
    def convert_from_url(self, url, inline_pdf=False, file_name=None):
        payload = self._make_url_payload(url, inline_pdf=inline_pdf, file_name=file_name)
        return self._make_request(API2PDF_LIBREOFFICE_CONVERT, payload)

class Api2PdfResponse(object):
    def __init__(self, headers, endpoint, payload_as_json, response):
        self.headers = headers
        self.endpoint = endpoint
        self.payload_as_json = payload_as_json
        self._result = json.loads(response.text)

    @property
    def request(self):
        request_info = {
            'headers': self.headers,
            'endpoint': self.endpoint,
            'payload': self.payload_as_json,
        }
        return request_info

    @property
    def result(self):
        return self._result

    def download_pdf(self):
        USERAGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        if self.result['success']:
            downloaded_pdf = requests.get(self.result['pdf'], headers=USERAGENT)
            data = downloaded_pdf.content
            return data
        else:
            raise FileNotFoundError("PDF never generated " + self.result['error'])

    def __str__(self):
        return """
---- API2PDF REQUEST ----
- Headers: {0}
- Endpoint: {1}
- Payload:
{2}
---- API2PDF RESPONSE ----
{3}
""".format(self.headers, self.endpoint, self.payload_as_json, self.result)
