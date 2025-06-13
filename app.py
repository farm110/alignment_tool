import streamlit as st
import pandas as pd
import io
import time
import gc
import os
from datetime import datetime

# Set page config for faster loading
st.set_page_config(
    page_title="Document Alignment Tool",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'alignment_results' not in st.session_state:
    st.session_state.alignment_results = None

@st.cache_data
def load_file(file):
    """Load a file into a pandas DataFrame with robust error handling."""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Try different encodings and parameters
        encodings = ['utf-8', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(
                        file,
                        encoding=encoding,
                        on_bad_lines='skip',
                        engine='python',
                        memory_map=False
                    )
                else:  # Excel files
                    df = pd.read_excel(
                        file,
                        engine='openpyxl'
                    )
                if not df.empty:
                    return df
            except Exception:
                file.seek(0)
                continue
        
        # If all attempts fail, try with more lenient parameters
        file.seek(0)
        if file.name.endswith('.csv'):
            df = pd.read_csv(
                file,
                encoding='latin1',
                on_bad_lines='skip',
                engine='python',
                memory_map=False,
                sep=None,
                skipinitialspace=True
            )
        else:
            df = pd.read_excel(file, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error loading file {file.name}: {str(e)}")
        return None

@st.cache_data
def align_documents(template_df, input_df, key_column):
    """Align documents based on the key column"""
    try:
        # Convert column to string type for consistent comparison
        template_df[key_column] = template_df[key_column].astype(str)
        input_df[key_column] = input_df[key_column].astype(str)
        
        merged_df = pd.merge(template_df, input_df, on=key_column, how='outer', suffixes=('_template', '_input'))
        matching_rows = merged_df.dropna(subset=[f'{key_column}'])
        template_only = merged_df[merged_df[f'{key_column}_input'].isna()]
        input_only = merged_df[merged_df[f'{key_column}_template'].isna()]
        
        # Clean up memory
        gc.collect()
        
        return matching_rows, template_only, input_only
    except Exception as e:
        st.error(f"Error aligning documents: {str(e)}")
        return None, None, None

def create_excel_output(matching_rows, template_only, input_only):
    """Create an Excel file with multiple sheets"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        matching_rows.to_excel(writer, sheet_name='Matching Rows', index=False)
        template_only.to_excel(writer, sheet_name='Template Only', index=False)
        input_only.to_excel(writer, sheet_name='Input Only', index=False)
    return output.getvalue()

def main():
    st.title("Document Alignment Tool")
    st.write("Upload a template document and one or more input documents to align them based on a key column.")
    
    # Template file upload
    template_file = st.file_uploader("Upload Template Document (CSV or Excel)", type=['csv', 'xlsx', 'xls'])
    
    if template_file:
        template_df = load_file(template_file)
        if template_df is not None:
            st.write("Template Preview:")
            st.dataframe(template_df.head())
            
            # Input files upload
            input_files = st.file_uploader("Upload Input Documents (CSV or Excel)", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True)
            
            if input_files:
                # Key column selection
                key_column = st.selectbox("Select Key Column for Alignment", template_df.columns)
                
                if st.button("Align Documents"):
                    with st.spinner('Processing documents...'):
                        start_time = time.time()
                        results = []
                        
                        for input_file in input_files:
                            input_df = load_file(input_file)
                            if input_df is not None:
                                # Align documents
                                matching_rows, template_only, input_only = align_documents(template_df, input_df, key_column)
                                
                                if matching_rows is not None:
                                    # Create Excel output
                                    excel_data = create_excel_output(matching_rows, template_only, input_only)
                                    results.append((input_file.name, matching_rows, template_only, input_only, excel_data))
                                    
                                    # Display results in tabs
                                    st.write(f"Results for {input_file.name}:")
                                    tab1, tab2, tab3 = st.tabs(["Matching Rows", "Template Only", "Input Only"])
                                    
                                    with tab1:
                                        st.dataframe(matching_rows)
                                    with tab2:
                                        st.dataframe(template_only)
                                    with tab3:
                                        st.dataframe(input_only)
                        
                        end_time = time.time()
                        
                        if results:
                            st.session_state.alignment_results = results
                            st.success(f"Processing completed in {end_time - start_time:.2f} seconds")
                            
                            # Provide download links
                            st.write("Download Results:")
                            for filename, _, _, _, excel_data in results:
                                st.download_button(
                                    label=f"Download {filename} results",
                                    data=excel_data,
                                    file_name=f"alignment_results_{filename}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.error("No results found")

if __name__ == "__main__":
    main() 