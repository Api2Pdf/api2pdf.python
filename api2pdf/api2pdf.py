import requests
import json

API2PDF_BASE_ENDPOINT = 'https://v2018.api2pdf.com'
API2PDF_MERGE_ENDPOINT = API2PDF_BASE_ENDPOINT + '/merge'
API2PDF_WKHTMLTOPDF_HTML = API2PDF_BASE_ENDPOINT + '/wkhtmltopdf/html'
API2PDF_WKHTMLTOPDF_URL = API2PDF_BASE_ENDPOINT + '/wkhtmltopdf/url'
API2PDF_CHROME_HTML = API2PDF_BASE_ENDPOINT + '/chrome/html'
API2PDF_CHROME_URL = API2PDF_BASE_ENDPOINT + '/chrome/url'
API2PDF_LIBREOFFICE_CONVERT = API2PDF_BASE_ENDPOINT + '/libreoffice/convert'

class Api2Pdf(object):
    def __init__(self, api_key):
        self.api_key = api_key

    @property
    def WkHtmlToPdf(self):
        return Api2Pdf_WkHtmlToPdf(self.api_key)

    @property
    def HeadlessChrome(self):
        return Api2Pdf_HeadlessChromeToPdf(self.api_key)

    @property
    def LibreOffice(self):
        return Api2Pdf_LibreOffice(self.api_key)

    def merge(self, list_of_urls):
        return self._make_request(API2PDF_MERGE_ENDPOINT, list_of_urls)

    def _make_html_payload(self, html, **options):
        payload = {
            'html': html,
        }
        if options != None:
            payload['options'] = options
        return payload

    def _make_url_payload(self, url, **options):
        payload = {
            'url': url
        }
        if options != None:
            payload['options'] = options
        return payload

    def _make_request(self, endpoint, payload):
        headers = {'Authorization': self.api_key}
        payload_as_json = json.dumps(payload)
        response = requests.post(endpoint, data=payload_as_json, headers=headers)
        return Api2PdfResponse(headers, endpoint, payload, response)

class Api2Pdf_WkHtmlToPdf(Api2Pdf):
    def convert_from_html(self, html, **options):
        payload = self._make_html_payload(html, **options)
        return self._make_request(API2PDF_WKHTMLTOPDF_HTML, payload)
    
    def convert_from_url(self, url, **options):
        payload = self._make_url_payload(url, **options)
        return self._make_request(API2PDF_WKHTMLTOPDF_URL, payload)

class Api2Pdf_HeadlessChromeToPdf(Api2Pdf):
    def convert_from_html(self, html, **options):
        payload = self._make_html_payload(html, **options)
        return self._make_request(API2PDF_CHROME_HTML, payload)
    
    def convert_from_url(self, url, **options):
        payload = self._make_url_payload(url, **options)
        return self._make_request(API2PDF_CHROME_URL, payload)

class Api2Pdf_LibreOffice(Api2Pdf):
    def convert_from_url(self, url):
        payload = self._make_url_payload(url)
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
            downloaded_pdf = requests.get(pdf_response['pdf'], headers=USERAGENT)
            data = download_response.content
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
