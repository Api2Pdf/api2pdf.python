import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="api2pdf",
    version="0.0.7",
    author="Zack Schwartz",
    author_email="support@api2pdf.com",
    description="Wrapper for api2pdf.com library for converting html, urls, and word documents to pdf",
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