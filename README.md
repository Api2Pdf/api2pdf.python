# api2pdf.python
Python bindings for [Api2Pdf REST API](https://www.api2pdf.com/documentation/v2) 

Api2Pdf.com is a powerful REST API for instantly generating PDF and Office documents from HTML, URLs, Microsoft Office Documents (Word, Excel, PPT), Email files, and images. You can generate image preview or thumbnail of a PDF, office document, or email file. The API also supports merge / concatenation of two or more PDFs, setting passwords on PDFs, and adding bookmarks to PDFs. Api2Pdf is a wrapper for popular libraries such as **wkhtmltopdf**, **Headless Chrome**, **PdfSharp**, and **LibreOffice**.

- [Installation](#installation)
- [Resources](#resources)
- [Authorization](#authorization)
- [Usage](#usage)
- [FAQ](https://www.api2pdf.com/faq)


## <a name="installation"></a>Add a dependency

### PyPI

Run the pip command for installing the client `pip install api2pdf`

## <a name="resources"></a>Resources

Resources this API supports:

- [wkhtmltopdf](#wkhtmltopdf)
- [Headless Chrome](#chrome)
- [LibreOffice](#libreoffice)
- [Merge / Concatenate PDFs](#merge)
- [Helper Methods](#helpers)

## <a name="authorization"></a>Authorization

### Acquire API Key

Create an account at [portal.api2pdf.com](https://portal.api2pdf.com/register) to get your API key.
    
## <a name="#usage"></a>Usage

### Initialize the Client

All usage starts by calling the import command and initializing the client by passing your API key as a parameter to the constructor.

    from api2pdf import Api2Pdf
    
    a2p_client = Api2Pdf('YOUR-API-KEY')

Once you initialize the client, you can make calls like so:

    api_response = a2p_client.Chrome.html_to_pdf('<p>Hello, World</p>')
    print(api_response.result)
    
### Result Object

An `Api2PdfResponse` object is returned from every API call. Call the `result` attribute to retrieve the data. If a call is unsuccessful then `success` will show False and the `error` will provide the reason for failure. Additional attributes include the total data usage in, out, and the cost for the API call, typically very small fractions of a penny.

    {
	    'FileUrl': 'https://link-to-pdf-only-available-for-24-hours',
	    'MbOut': 0.08830547332763672,
        'Seconds': 9.43,
	    'Cost': 0.00017251586914062501,
	    'Success': True,
	    'Error': None,
	    'ResponseId': '6e46637a-650d-46d5-af0b-3d7831baccbb'
    }

For debugging, you can print the `Api2PdfResponse` object to see the request and response data.

    api_response = a2p_client.Chrome.html_to_pdf('<p>Hello, World</p>')
    print(api_response)
    
Output:

    ---- API2PDF REQUEST ----
    - Headers: {'Authorization': 'YOUR-API-KEY'}
    - Endpoint: https://v2018.api2pdf.com/chrome/html
    - Payload:
    {'html': '<p>Hello, World</p>'}
    ---- API2PDF RESPONSE ----
    {'ResponseId': '5ef656a7-2856-43f4-aae3-7b580b0e0421', 'MbOut': 0.012622, 'Cost': 0.000257195288, 'Seconds': 1.208, 'Error': None, 'Success': True, 'FileUrl': 'https://storage.googleapis.com/a2p-v2-storage/5ef656a7-2856-43f4-aae3-7b580b0e0421'}

    
### <a name="wkhtmltopdf"></a> wkhtmltopdf

**Convert HTML to PDF**

    api_response = a2p_client.WkHtml.html_to_pdf('<p>Hello, World</p>')
    
**Convert HTML to PDF (ldownload PDF as a file and specify a file name)**

    api_response = a2p_client.WkHtml.html_to_pdf('<p>Hello, World</p>', inline_pdf=True, file_name='test.pdf')
    
**Convert HTML to PDF (use keyword arguments for advanced wkhtmltopdf settings)**
[View full list of wkhtmltopdf options available.](https://www.api2pdf.com/documentation/advanced-options-wkhtmltopdf/)

    options = {
        'orientation': 'landscape',
        'pageSize': 'A4'
    }
    api_response = a2p_client.WkHtml.html_to_pdf('<p>Hello, World</p>', **options)

**Convert URL to PDF**

    api_response = a2p_client.WkHtml.url_to_pdf('http://www.api2pdf.com')
    
**Convert URL to PDF (download PDF as a file and specify a file name)**

    api_response = a2p_client.WkHtml.url_to_pdf('http://www.api2pdf.com', inline=False, file_name='test.pdf')
    
**Convert URL to PDF (use keyword arguments for advanced wkhtmltopdf settings)**
[View full list of wkhtmltopdf options available.](https://www.api2pdf.com/documentation/advanced-options-wkhtmltopdf/)

    options = {
        'orientation': 'landscape',
        'pageSize': 'A4'
    }
    api_response = a2p_client.WkHtml.url_to_pdf('http://www.api2pdf.com', **options)


---

## <a name="chrome"></a>Headless Chrome

**Convert HTML to PDF**

    api_response = a2p_client.Chrome.html_to_pdf('<p>Hello, World</p>')
    
**Convert HTML to PDF (download PDF as a file and specify a file name)**

    api_response = a2p_client.Chrome.html_to_pdf('<p>Hello, World</p>', inline=False, file_name='test.pdf')
    
**Convert HTML to PDF (use keyword arguments for advanced Headless Chrome settings)**
[View full list of Headless Chrome options available.](https://www.api2pdf.com/documentation/advanced-options-headless-chrome/)

    options = {
        'landscape': True
    }
    api_response = a2p_client.Chrome.html_to_pdf('<p>Hello, World</p>', **options)

**Convert URL to PDF**

    api_response = a2p_client.Chrome.url_to_pdf('http://www.api2pdf.com')
    
**Convert URL to PDF (download PDF as a file and specify a file name)**

    api_response = a2p_client.Chrome.url_to_pdf('http://www.api2pdf.com', inline=False, file_name='test.pdf')
    
**Convert URL to PDF (use keyword arguments for advanced Headless Chrome settings)**
[View full list of Headless Chrome options available.](https://www.api2pdf.com/documentation/advanced-options-headless-chrome/)

    options = {
        'landscape': True
    }
    api_response = a2p_client.Chrome.url_to_pdf('http://www.api2pdf.com', **options)
    
**Convert HTML to Image**

    api_response = a2p_client.Chrome.html_to_image('<p>Hello, World</p>')

**Convert URL to Image**

    api_response = a2p_client.Chrome.url_to_image('http://www.api2pdf.com')
---

## <a name="libreoffice"></a>LibreOffice

Convert any office file to PDF, image file to PDF, email file to PDF, HTML to Word, HTML to Excel, and PDF to HTML. Any file that can be reasonably opened by LibreOffice should be convertible. Additionally, we have an endpoint for generating a *thumbnail* of the first page of your PDF or Office Document. This is great for generating an image preview of your files to users.

You must provide a url to the file. Our engine will consume the file at that URL and convert it.

**Convert Microsoft Office Document or Image to PDF**

    api_response = a2p_client.LibreOffice.any_to_pdf('https://www.api2pdf.com/wp-content/themes/api2pdf/assets/samples/sample-word-doc.docx')
    
**Convert Microsoft Office Document or Image to PDF (download PDF as a file and specify a file name)**

    api_response = a2p_client.LibreOffice.any_to_pdf('https://www.api2pdf.com/wp-content/themes/api2pdf/assets/samples/sample-word-doc.docx', inline=False, file_name='test.pdf')

**Thumbnail or Image Preview of a PDF or Office Document or Email file**

    api_response = a2p_client.LibreOffice.thumbnail('https://www.api2pdf.com/wp-content/themes/api2pdf/assets/samples/sample-word-doc.docx')

**Convert HTML to Microsoft Word or Docx**

    api_response = a2p_client.LibreOffice.html_to_docx('http://www.api2pdf.com/wp-content/uploads/2021/01/sampleHtml.html')

**Convert HTML to Microsoft Excel or Xlsx**

    api_response = a2p_client.LibreOffice.html_to_xlsx('http://www.api2pdf.com/wp-content/uploads/2021/01/sampleTables.html')

**Convert PDF to HTML**

    api_response = a2p_client.LibreOffice.pdf_to_html('http://www.api2pdf.com/wp-content/uploads/2021/01/1a082b03-2bd6-4703-989d-0443a88e3b0f-4.pdf')
    
---
    
## <a name="merge"></a>PdfSharp - Merge / Concatenate Two or More PDFs, Add bookmarks to pdfs, add passwords to pdfs

To use the merge endpoint, supply a list of urls to existing PDFs. The engine will consume all of the PDFs and merge them into a single PDF, in the order in which they were provided in the list.

**Merge PDFs from list of URLs to existing PDFs**

    links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    merge_result = a2p_client.PdfSharp.merge(links_to_pdfs)

**Merge PDFs from list of URLs to existing PDFs (download PDF as a file and specify a file name)**

    links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    merge_result = a2p_client.PdfSharp.merge(links_to_pdfs, inline=True, file_name='test.pdf')

**Add bookmarks to existing PDF**

    url = 'https://link-to-pdf'
    bookmarks = [
        { 'Page': 0, 'Title': 'Introduction' },
        { 'Page': 1, 'Title': 'Second page' }
    ]
    response = a2p.PdfSharp.add_bookmarks(url, bookmarks)

**Add password to existing PDF**

    url = 'https://link-to-pdf'
    password = 'hello'
    response = a2p.PdfSharp.add_password(url, password)

---
    
## <a name="helpers"></a>Helper Methods

**Api2PdfResponse: download_file()**

On any `Api2PdfResponse` that succesfully generated a pdf, you can use the handy `download_file()` method to download the pdf to a file-like object which you can then save to your local cache. If the pdf generation was unsuccessful, it will throw a FileNotFoundException.

```
from api2pdf import Api2Pdf
a2p_client = Api2Pdf('YOUR-API-KEY')
    
# merge pdfs
links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
merge_result = a2p_client.PdfSharp.merge(links_to_pdfs)
    
pdf_as_file_object = merge_result.download_file()
```

**Delete a PDF on Command with delete(response_id)**

By default, Api2Pdf will automatically delete your PDFs after 24 hours. If you have higher security requirements and need to delete the PDFs at-will, you can do so by calling the `delete(response_id)` method on the Api2Pdf object where `response_id` parameter comes from the responseId attribute in the Api2PdfResponse result.

```
from api2pdf import Api2Pdf
a2p_client = Api2Pdf('YOUR-API-KEY')
    
# generate a pdf
api_response = a2p_client.Chrome.html_to_pdf('<p>Hello World</p>')
response_id = api_response.result['ResponseId']

# delete the pdf
a2p_client.delete(response_id)
```
