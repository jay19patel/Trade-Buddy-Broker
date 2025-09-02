"""
Setup script for Trade Buddy SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trade-buddy-sdk",
    version="1.0.0",
    author="Trade Buddy Team",
    author_email="support@tradebuddy.com", 
    description="Production-ready broker SDK for paper trading with enterprise architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tradebuddy/trade-buddy-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "coverage>=7.0.0",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "trading", "paper-trading", "broker", "finance", "sdk", 
        "stocks", "investment", "portfolio", "orders"
    ],
    project_urls={
        "Bug Reports": "https://github.com/tradebuddy/trade-buddy-sdk/issues",
        "Source": "https://github.com/tradebuddy/trade-buddy-sdk",
        "Documentation": "https://github.com/tradebuddy/trade-buddy-sdk#readme",
    },
)