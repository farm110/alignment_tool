import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Tuple, List

def load_excel_or_csv(file: BytesIO) -> pd.DataFrame:
    """Load data from Excel or CSV file into a DataFrame."""
    try:
        if file.name.lower().endswith(('.xls', '.xlsx')):
            return pd.read_excel(file)
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error loading file {file.name}: {str(e)}")
        return None

def compare_dataframes(template: pd.DataFrame, input_df: pd.DataFrame, key_col: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compare two DataFrames and return matching, template-only, and input-only rows."""
    try:
        # Ensure key column exists in both DataFrames
        if key_col not in template.columns:
            raise ValueError(f"Key column '{key_col}' not found in template file")
        if key_col not in input_df.columns:
            raise ValueError(f"Key column '{key_col}' not found in input file")

        # Perform merge
        merged = pd.merge(
            template,
            input_df,
            on=key_col,
            how='outer',
            indicator=True
        )

        # Split results
        matching = merged[merged['_merge'] == 'both'].drop(columns=['_merge'])
        template_only = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
        input_only = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge'])

        return matching, template_only, input_only
    except Exception as e:
        st.error(f"Error comparing files: {str(e)}")
        return None, None, None

def save_to_excel(matching: pd.DataFrame, template_only: pd.DataFrame, input_only: pd.DataFrame, filename: str) -> BytesIO:
    """Save comparison results to Excel file."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        matching.to_excel(writer, sheet_name='Matching', index=False)
        template_only.to_excel(writer, sheet_name='Template_Only', index=False)
        input_only.to_excel(writer, sheet_name='Input_Only', index=False)
    return output

def main():
    st.set_page_config(page_title="Document Alignment Tool", layout="wide")
    st.title("📄 Document Alignment Tool")

    # File upload section
    st.sidebar.header("Upload Files")
    template_file = st.sidebar.file_uploader(
        "Upload template file (Excel/CSV)",
        type=['xlsx', 'xls', 'csv'],
        help="Upload your template file first"
    )

    # Process template file
    template_df = None
    if template_file:
        template_df = load_excel_or_csv(template_file)
        if template_df is not None:
            st.sidebar.success(f"Template loaded: {len(template_df)} rows")
            
            # Column selection
            key_column = st.sidebar.selectbox(
                "Select key column for alignment",
                options=template_df.columns.tolist(),
                help="Choose the column that will be used to match records"
            )

            # Input file upload
            input_files = st.sidebar.file_uploader(
                "Upload input files (Excel/CSV)",
                type=['xlsx', 'xls', 'csv'],
                accept_multiple_files=True,
                help="Upload one or more files to compare with the template"
            )

            # Process input files
            if input_files:
                for input_file in input_files:
                    st.subheader(f"Processing {input_file.name}")
                    
                    # Load input file
                    input_df = load_excel_or_csv(input_file)
                    if input_df is None:
                        continue

                    # Compare files
                    matching, template_only, input_only = compare_dataframes(
                        template_df, input_df, key_column
                    )

                    if matching is not None:
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write("**Matching rows:**", len(matching))
                            st.dataframe(matching)
                        with col2:
                            st.write("**Only in template:**", len(template_only))
                            st.dataframe(template_only)
                        with col3:
                            st.write("**Only in input:**", len(input_only))
                            st.dataframe(input_only)

                        # Download button
                        output = save_to_excel(matching, template_only, input_only, input_file.name)
                        st.download_button(
                            label="Download results as Excel",
                            data=output.getvalue(),
                            file_name=f"alignment_{input_file.name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

if __name__ == "__main__":
    main()
