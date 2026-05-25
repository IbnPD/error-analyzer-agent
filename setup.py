"""
Error Analyzer Agent - Setup Script

AI-powered error log and stack trace analyzer using MiMo API.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="error-analyzer-agent",
    version="1.0.0",
    description="AI-powered error log and stack trace analyzer using MiMo API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Error Analyzer Agent",
    author_email="agent@example.com",
    url="https://github.com/error-analyzer-agent/error-analyzer-agent",
    license="MIT",
    packages=find_packages(exclude=["tests*", "examples*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "error-analyzer=analyzer:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="error analyzer stack trace debugging AI mimo",
)
