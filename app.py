import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page config for faster loading
st.set_page_config(
    page_title="Document Alignment Tool",
    page_icon="📊",
    layout="wide"
)

# Cache the file reading function
@st.cache_data
def read_file(file):
    """Read CSV or Excel file and return a DataFrame"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file, engine='openpyxl')
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

# Cache the alignment function
@st.cache_data
def align_documents(template_df, input_df, key_column):
    """Align documents based on the key column"""
    try:
        merged_df = pd.merge(template_df, input_df, on=key_column, how='outer', suffixes=('_template', '_input'))
        matching_rows = merged_df.dropna(subset=[f'{key_column}'])
        template_only = merged_df[merged_df[f'{key_column}_input'].isna()]
        input_only = merged_df[merged_df[f'{key_column}_template'].isna()]
        return matching_rows, template_only, input_only
    except Exception as e:
        st.error(f"Error aligning documents: {str(e)}")
        return None, None, None

def save_to_excel(df, filename):
    """Save DataFrame to Excel file"""
    try:
        df.to_excel(filename, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving to Excel: {str(e)}")
        return False

def main():
    st.title("Document Alignment Tool")
    st.write("Upload a template document and one or more input documents to align them based on a key column.")
    
    # Create output directory if it doesn't exist
    output_dir = "alignment_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Template file upload
    template_file = st.file_uploader("Upload Template Document (CSV or Excel)", type=['csv', 'xlsx', 'xls'])
    
    if template_file:
        template_df = read_file(template_file)
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
                        results_files = []
                        
                        for input_file in input_files:
                            input_df = read_file(input_file)
                            if input_df is not None:
                                # Align documents
                                matching_rows, template_only, input_only = align_documents(template_df, input_df, key_column)
                                
                                if matching_rows is not None:
                                    # Save results
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    base_filename = os.path.join(output_dir, f'alignment_results_{timestamp}')
                                    
                                    # Save each DataFrame separately
                                    if save_to_excel(matching_rows, f"{base_filename}_matching.xlsx"):
                                        results_files.append(f"{base_filename}_matching.xlsx")
                                    if save_to_excel(template_only, f"{base_filename}_template_only.xlsx"):
                                        results_files.append(f"{base_filename}_template_only.xlsx")
                                    if save_to_excel(input_only, f"{base_filename}_input_only.xlsx"):
                                        results_files.append(f"{base_filename}_input_only.xlsx")
                                    
                                    # Display results in tabs
                                    tab1, tab2, tab3 = st.tabs(["Matching Rows", "Template Only", "Input Only"])
                                    
                                    with tab1:
                                        st.dataframe(matching_rows)
                                    with tab2:
                                        st.dataframe(template_only)
                                    with tab3:
                                        st.dataframe(input_only)
                        
                        if results_files:
                            # Provide download links
                            st.success("Processing complete!")
                            st.write("Download Results:")
                            for result_file in results_files:
                                with open(result_file, 'rb') as f:
                                    st.download_button(
                                        label=f"Download {os.path.basename(result_file)}",
                                        data=f,
                                        file_name=os.path.basename(result_file),
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )

if __name__ == "__main__":
    main() 