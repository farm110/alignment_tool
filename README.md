# Document Alignment Tool

This Streamlit application helps you align and compare multiple documents (CSV or Excel files) based on a common key column.

## Features

- Upload a template document and multiple input documents
- Align documents based on a selected key column
- View matching and non-matching rows
- Download results in Excel format with multiple sheets
- Support for both CSV and Excel files

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

## How to Use

1. Upload a template document (CSV or Excel file)
2. Upload one or more input documents to compare with the template
3. Select the key column that will be used for alignment
4. Click "Align Documents" to process the files
5. View the results in the web interface
6. Download the results as Excel files

## Output Format

The results will be saved in Excel files with three sheets:
- Matching Rows: Rows that match between the template and input documents
- Template Only: Rows that exist only in the template document
- Input Only: Rows that exist only in the input document

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- Openpyxl 