#!/usr/bin/env python3
"""Setup configuration for LeetCode CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="leetcode-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based CLI tool to interact with LeetCode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elxecutor/leetcode-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "rich>=12.0.0",
        "typer>=0.7.0",
        "click>=8.0.0",
        "httpx>=0.24.0",
        "beautifulsoup4>=4.11.0",
        "markdown>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "leetcode=leetcode_cli.main:app",
        ],
    },
)
