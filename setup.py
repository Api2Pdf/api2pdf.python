import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="api2pdf",
    version="2.1.0",
    author="Zack Schwartz",
    author_email="support@api2pdf.com",
    description="This client library is a wrapper for the Api2Pdf.com REST API. See full REST api documentation at https://www.api2pdf.com/documentation/v2. Api2Pdf is a powerful API that supports HTML to PDF, URL to PDF, HTML to Image, URL to Image, Thumbnail / image preview of an Office file, Office files (Word to PDF), HTML to Docx, HTML to excel, PDF to HTML, merge PDFs together, add bookmarks to PDFs, add passwords to PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/api2pdf/api2pdf.python",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)