# trading-assistant-project/trading-assistant/setup.py
from setuptools import setup, find_packages

setup(
    name="trading-assistant",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "anthropic",
        "python-dotenv",
        "yfinance",
        "pandas",
        "numpy",
        "ta"
    ]
)