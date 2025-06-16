import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Document Alignment Tool", layout="wide")

@st.cache_data
def load_dataframe(uploaded_file: BytesIO, sheet_name: str = None):
    """
    Load an Excel/CSV file into a DataFrame, cached by contents and sheet.
    """
    if uploaded_file.name.lower().endswith(('.xls', '.xlsx')):
        return pd.read_excel(uploaded_file, sheet_name=sheet_name)
    else:
        return pd.read_csv(uploaded_file)

@st.cache_data
def align_data(template_df: pd.DataFrame, input_df: pd.DataFrame, key: str):
    """
    Align two DataFrames on the key column. Returns matching, template-only, and input-only.
    """
    # Ensure we're working with DataFrames
    if isinstance(template_df, dict):
        template_df = pd.DataFrame(template_df)
    if isinstance(input_df, dict):
        input_df = pd.DataFrame(input_df)
    
    if not isinstance(template_df, pd.DataFrame) or not isinstance(input_df, pd.DataFrame):
        raise TypeError("Both template_df and input_df must be pandas DataFrames")
    
    merged = template_df.merge(input_df, on=key, how='outer', indicator=True)
    matching = merged[merged['_merge'] == 'both'].drop(columns=['_merge'])
    template_only = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
    input_only = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge'])
    return matching, template_only, input_only

st.title("📄 Document Alignment Tool")

# Sidebar: upload files
template_file = st.sidebar.file_uploader("Upload template CSV/Excel", type=['csv', 'xls', 'xlsx'])
input_files = st.sidebar.file_uploader("Upload input CSV/Excel", type=['csv', 'xls', 'xlsx'], accept_multiple_files=True)

if template_file:
    template_df = load_dataframe(template_file)
    st.sidebar.write(f"Template has {len(template_df)} rows.")
    
    # Create select box for key column based on template columns
    key_column = st.sidebar.selectbox(
        "Select key column for alignment",
        options=template_df.columns.tolist(),
        help="Choose the column that will be used to match records between files"
    )
    
    if input_files and key_column:
        for file in input_files:
            input_df = load_dataframe(file)
            st.sidebar.write(f"Processing {file.name} ({len(input_df)} rows)")

            # Perform alignment
            matching, tem_only, inp_only = align_data(template_df, input_df, key_column)

            st.subheader(f"Results for {file.name}")
            st.write("**Matching rows:**", matching)
            st.write("**Only in template:**", tem_only)
            st.write("**Only in input:**", inp_only)

            # Download results button
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                matching.to_excel(writer, sheet_name='Matching', index=False)
                tem_only.to_excel(writer, sheet_name='Template_Only', index=False)
                inp_only.to_excel(writer, sheet_name='Input_Only', index=False)
            st.download_button(
                label="Download results as Excel",
                data=output.getvalue(),
                file_name=f"alignment_{file.name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
