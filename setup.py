from setuptools import setup

setup(
    name="document-alignment-tool",
    version="0.1.0",
    install_requires=[
        "streamlit==1.32.0",
        "pandas==2.2.1",
        "numpy==1.24.4",
        "xlsxwriter==3.1.9",
        "watchdog==3.0.0",
    ],
    python_requires=">=3.9",
) 