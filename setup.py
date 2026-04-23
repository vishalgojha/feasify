from setuptools import setup, find_packages

setup(
    name="feasify",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "cachetools>=5.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "psycopg2-binary>=2.9.9",
        ]
    },
    python_requires=">=3.9",
    author="Feasify Team",
    author_email="team@feasify.com",
    description="Real estate cost estimation tool for Mumbai/Pune regions",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/feasify/feasify",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
