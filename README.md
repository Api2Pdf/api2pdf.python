# Api2Pdf - Python
[Api2Pdf.com](https://www.api2pdf.com) | [Docs](https://www.api2pdf.com/documentation) 

## What is Api2Pdf?
Api2Pdf.com is a service for instantly generating PDFs.

- [Get Started](#get-started)
- [HTML](#convert-from-html)
- [URLs](#convert-from-urls)
- [Microsoft Office documents (Word, Excel, Powerpoint)](#convert-from-office)
- [Images](#convert-from-office)
- [Merge / Concatenate two or more PDFs](#merge)
- [Helper Methods](#helper-methods)
- [FAQ](#faq)

Api2Pdf provides access to **wkhtmltopdf**, **Headless Chrome**, and **LibreOffice**, along with the ability to merge / concatenate PDFs together.



## <a name="get-started"></a>Get Started
This python library provides convenient methods for accessing the REST API [documented here](https://www.api2pdf.com/documentation/).

### Acquire API Key
1. Create an account and login at [portal.api2pdf.com](https://portal.api2pdf.com)
2. Add a balance to your account (no monthly commitment, sign up with as little as $1)
3. Create an application and grab your API Key

### Install
    pip install api2pdf
    
### Usage

    from api2pdf import Api2Pdf
    
    a2p = Api2Pdf('YOUR-API-KEY')
    api_response = a2p.HeadlessChrome.convert_from_html('<p>Hello, World</p>')
    print(api_response.result)
    
### Sample Result

An `Api2PdfResponse` object is returned from every API call. Call the `result` attribute to retrieve the data. If a call is unsuccessful then `success` will show False and the `error` will provide the reason for failure. Additional attributes include the total data usage in, out, and the cost for the API call.

    {
	    'pdf': 'https://link-to-pdf-only-available-for-24-hours',
	    'mbIn': 0.08421039581298828,
	    'mbOut': 0.08830547332763672,
	    'cost': 0.00017251586914062501,
	    'success': True,
	    'error': None,
	    'responseId': '6e46637a-650d-46d5-af0b-3d7831baccbb'
    }

For debugging, you can simply print the `Api2PdfResponse` object to see the request and response data.

    links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    merge_result = a2p.merge(links_to_pdfs)
    print(api_response)
    
Output:

    ---- API2PDF REQUEST ----
    - Headers: {'Authorization': 'f8bd6792-f1cd-42df-9bf9-f7a35e59362f'}
    - Endpoint: https://v2018.api2pdf.com/merge
    - Payload:
    ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    ---- API2PDF RESPONSE ----
    {'pdf': 'https://link-to-pdf-only-available-for-24-hours', 'mbIn': 0.08421039581298828, 'mbOut': 0.08830547332763672, 'cost': 0.00017251586914062501, 'success': True, 'error': None, 'responseId': '163c4d25-25d7-4b82-bf50-907597d2ad46'}

    
## Documentation

### <a name="convert-from-html"></a>Convert HTML to PDF

We support both **wkhtmltopdf** and **Headless Chrome** with the endpoint to convert raw html to PDFs. Both endpoints allow you to pass keyword arguments that are options available for their respective libraries.

- [wkhtmltopdf options](https://www.api2pdf.com/documentation/advanced-options-wkhtmltopdf/)
- [headless chrome options](https://www.api2pdf.com/documentation/advanced-options-headless-chrome/)

##### HeadlessChrome.convert_from_html(html, inline_pdf=True, file_name=None, **options)
##### WkHtmlToPdf.convert_from_html(html, inline_pdf=True, file_name=None, **options)

    from api2pdf import Api2Pdf
    a2p = Api2Pdf('YOUR-API-KEY')
    
    # headless chrome
    headless_chrome_result = a2p.HeadlessChrome.convert_from_html('<p>Hello World</p>')
    print(headless_chrome_result.result)
    
    # wkhtmltopdf
    wkhtmltopdf_result = a2p.WkHtmlToPdf.convert_from_html('<p>Hello World</p>')
    print(wkhtmltopdf_result.result)
    
### <a name="convert-from-url"></a>Convert URL to PDF

We support both wkhtmltopdf and Headless Chrome with the endpoint to convert urls to PDFs. Both endpoints allow you to pass keyword arguments that are options available for their respective libraries.

- [wkhtmltopdf options](https://www.api2pdf.com/documentation/advanced-options-wkhtmltopdf/)
- [headless chrome options](https://www.api2pdf.com/documentation/advanced-options-headless-chrome/)

##### HeadlessChrome.convert_from_url(url, inline_pdf=True, file_name=None, **options)

##### WkHtmlToPdf.convert_from_url(url, inline_pdf=True, file_name=None, **options)

    from api2pdf import Api2Pdf
    a2p = Api2Pdf('YOUR-API-KEY')
    
    # headless chrome
    headless_chrome_result = a2p.HeadlessChrome.convert_from_url('https://LINK-TO-YOUR-WEBSITE')
    print(headless_chrome_result.result)
    
    # wkhtmltopdf
    wkhtmltopdf_result = a2p.WkHtmlToPdf.convert_from_url('https://LINK-TO-YOUR-WEBSITE')
    print(wkhtmltopdf_result.result)
    
### <a name="convert-from-office"></a>Convert Microsoft Office Documents and Images to PDF

We use **LibreOffice** to convert the following formats to PDF:

- doc, docx, xls, xlsx, ppt, pptx, gif, jpg, png, bmp, rtf, txt, html

You must provide a url to the file. Our engine will consume the file at that URL and convert it to the PDF.

##### LibreOffice.convert_from_url(url, inline_pdf=True, file_name=None)

    from api2pdf import Api2Pdf
    a2p = Api2Pdf('YOUR-API-KEY')
    
    libreoffice_result = a2p.LibreOffice.convert_from_html('https://LINK-TO-YOUR-FILE')
    print(libreoffice_result.result)
    
### <a name="merge"></a>Merge / Concatenate Two or More PDFs

To use the merge endpoint, supply a list of urls to existing PDFs. The engine will consume all of the PDFs and merge them into a single PDF, in the order in which they were provided in the list.

##### merge(list_of_urls)
    
    from api2pdf import Api2Pdf
    a2p = Api2Pdf('YOUR-API-KEY')
    
    # merge pdfs
    links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    merge_result = a2p.merge(links_to_pdfs)
    print(merge_result.result)
    
### <a name="helper-methods"></a>Helper Methods

##### Api2PdfResponse: download_pdf()

On any `Api2PdfResponse` that succesfully generated a pdf, you can use the handy download_pdf() method to download the pdf to a file-like object which you can then save to your local cache. If the pdf generation was unsuccessful, it will throw a FileNotFoundException.

    from api2pdf import Api2Pdf
    a2p = Api2Pdf('YOUR-API-KEY')
    
    # merge pdfs
    links_to_pdfs = ['https://LINK-TO-PDF', 'https://LINK-TO-PDF']
    merge_result = a2p.merge(links_to_pdfs)
    
    pdf_as_file_object = merge_result.download_pdf()
    
    
## <a name="faq"></a>FAQ

#### How do you bill?
$1 will be deducted from your balance every month as long as you maintain an active account. This charge begins 30 days after your first sign up for the service. In addition, we charge $0.001 per megabyte (data in + data out). We require customers to maintain a positive balance on their account to use the service. You can turn off auto-recharge at any time and let your funds run out if you no longer wish to use the service. See our [pricing calculator](https://www.api2pdf.com/pricing/).

#### Do you offer free accounts?
The average customer spents about $2/month on our product. We do not have free accounts as this time. Feel free to check out alternatives and competitors.

#### Cancellation and refunds
We do not have any long term contracts. You can leave us at anytime with no further commitments. As our minimum cost is $1.00, we do not provide refunds.

#### Are there any limits?
Api2Pdf does not set any specific limits on PDF file size, however our system does have processing power limitations. Each PDF request is provided 3 GB of RAM to work with and 110 seconds to generate the PDF. We offer WKHTMLTOPDF, Headless Chrome, and LibreOffice to do conversions. Our platform will have the same limits as those underlying components. If the underlying component fails to convert to PDF, it will also fail via our service. Some examples are:

- Password protected PDFs
- Encrypted PDFs
- HTML that references erroneous content
- Protected Office Documents

#### How long are PDFs stored on Api2Pdf.com?
After generating a PDF via the API, you are provided with a link to the file. This link will hold the PDF for 24 hours. If you wish to keep your PDF long term, download the file to your local cache.
