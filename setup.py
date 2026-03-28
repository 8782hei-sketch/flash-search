from setuptools import setup, find_packages

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding='UTF-8') as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip()]

setup(
    name="flash-search",
    version="2.0.0",
    author="Tristan P.C",
    author_email="support@flash-search.dev",
    description="A fast, multi-source web search library with intelligent fallback and content extraction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/8782hei-sketch/flash-search",
    project_urls={
        "Bug Tracker": "https://github.com/8782hei-sketch/flash-search/issues",
        "Documentation": "https://github.com/8782hei-sketch/flash-search#flash-search",
        "Source Code": "https://github.com/8782hei-sketch/flash-search",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,
    keywords="search web-scraping information-gathering duckduckgo curl-cffi search engine",
)
