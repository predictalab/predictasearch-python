from pathlib import Path

from setuptools import find_packages, setup

parent_directory = Path(__file__).parent

setup(
    name="predictasearch",
    version="1.0.1",
    author="Predicta Lab",
    author_email="contact@predictalab.com",
    description="Python library and command-line utility for Predicta Search API",
    packages=find_packages(),
    long_description=(parent_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["requests >= 2.32.3"],
    python_requires=">=3.8",
    url="https://github.com/predictalab/predictasearch-python",
    project_urls={
        "Homepage": "https://github.com/predictalab/predictasearch-python",
        "Repository": "https://github.com/predictalab/predictasearch-python",
        "Issues": "https://github.com/predictalab/predictasearch-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
    ],
)
