from setuptools import setup, find_packages

setup(
    name="seo-audit-tool",
    version="1.0.0",
    author="Esteban Selvaggi",
    author_email="selvaggi.esteban@gmail.com",
    description="Herramienta profesional de auditoría SEO con 10 dimensiones de análisis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/selvaggiesteban/SEO_Audit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Marketing Professionals",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "google": [
            "google-api-python-client>=2.100.0",
            "google-auth>=2.23.0",
            "google-auth-oauthlib>=1.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "seo-audit=src.audit_engine:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/selvaggiesteban/SEO_Audit/issues",
        "Documentation": "https://github.com/selvaggiesteban/SEO_Audit#readme",
        "Source": "https://github.com/selvaggiesteban/SEO_Audit",
    },
)
