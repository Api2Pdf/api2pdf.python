import requests
import json

class Api2Pdf(object):
    def __init__(self, api_key, base_url='https://v2.api2pdf.com', tag=''):
        self.api_key = api_key
        self.tag = tag
        self.base_url = base_url

    @property
    def WkHtml(self):
        return Api2Pdf_WkHtml(self.api_key, self.base_url)

    @property
    def Chrome(self):
        return Api2Pdf_Chrome(self.api_key, self.base_url)

    @property
    def LibreOffice(self):
        return Api2Pdf_LibreOffice(self.api_key, self.base_url)

    @property
    def PdfSharp(self):
        return Api2Pdf_PdfSharp(self.api_key, self.base_url)

    def delete(self, response_id):
        headers = self.request_header
        endpoint = f'/file/{response_id}'.format(response_id=response_id)
        full_endpoint = self.base_url + endpoint
        response = requests.delete(full_endpoint, headers=headers)
        return Api2PdfResponse(headers, full_endpoint, '', response)

    def _build_base_payload(self, inline=True, file_name=None, **options):
        payload = {
            'inline': inline
        }
        if file_name != None:
            payload['fileName'] = file_name
        if options != None:
            payload['options'] = options
        return payload

    def _make_request(self, endpoint, payload):
        headers = self.request_header
        payload_as_json = json.dumps(payload)
        full_endpoint = self.base_url + endpoint
        response = requests.post(full_endpoint, data=payload_as_json, headers=headers)
        return Api2PdfResponse(headers, full_endpoint, payload, response)

    @property
    def request_header(self):
        header = {}
        header['Authorization'] = self.api_key
        if self.tag:
            header['Tag'] = self.tag
        return header

class Api2Pdf_WkHtml(Api2Pdf):
    def html_to_pdf(self, html, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['html'] = html
        return self._make_request('/wkhtml/pdf/html', payload)
    
    def url_to_pdf(self, url, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['url'] = url
        return self._make_request('/wkhtml/pdf/url', payload)

class Api2Pdf_Chrome(Api2Pdf):
    def html_to_pdf(self, html, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['html'] = html
        return self._make_request('/chrome/pdf/html', payload)
    
    def url_to_pdf(self, url, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['url'] = url
        return self._make_request('/chrome/pdf/url', payload)

    def html_to_image(self, html, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['html'] = html
        return self._make_request('/chrome/image/html', payload)
    
    def url_to_image(self, url, inline=True, file_name=None, **options):
        payload = self._build_base_payload(inline, file_name, **options)
        payload['url'] = url
        return self._make_request('/chrome/image/url', payload)

class Api2Pdf_LibreOffice(Api2Pdf):
    def any_to_pdf(self, url, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        return self._make_request('/libreoffice/any-to-pdf', payload)

    def thumbnail(self, url, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        return self._make_request('/libreoffice/thumbnail', payload)

    def pdf_to_html(self, url, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        return self._make_request('/libreoffice/pdf-to-html', payload)

    def html_to_docx(self, url, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        return self._make_request('/libreoffice/html-to-docx', payload)

    def html_to_xlsx(self, url, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        return self._make_request('/libreoffice/html-to-xlsx', payload)

class Api2Pdf_PdfSharp(Api2Pdf):
    def merge(self, urls, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['urls'] = urls
        return self._make_request('/pdfsharp/merge', payload)

    def add_bookmarks(self, url, bookmarks, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        payload['bookmarks'] = bookmarks
        return self._make_request('/pdfsharp/bookmarks', payload)

    def add_password(self, url, userpassword, ownerpassword=None, inline=True, file_name=None):
        payload = self._build_base_payload(inline, file_name)
        payload['url'] = url
        payload['userpassword'] = userpassword
        if ownerpassword != None:
            payload['ownerpassword'] = ownerpassword
        return self._make_request('/pdfsharp/password', payload)

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

    def download_file(self):
        USERAGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        if self.result['Success']:
            downloaded_file = requests.get(self.result['FileUrl'], headers=USERAGENT)
            data = downloaded_file.content
            return data
        else:
            raise FileNotFoundError("File never generated " + self.result['error'])

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
