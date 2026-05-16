"""
Setup script for RepoMesh AI.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repomesh-ai",
    version="0.1.0",
    author="RepoMesh Team",
    author_email="team@repomesh.ai",
    description="Multi-agent AI system for coordinated repository analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/repomesh/repomesh-ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "langgraph>=0.0.20",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "gitpython>=3.1.40",
        "chromadb>=0.4.22",
        "openai>=1.10.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "httpx>=0.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.1.0",
            "ruff>=0.1.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
    },
)

# Made with Bob
