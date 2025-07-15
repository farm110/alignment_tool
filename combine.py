import pandas as pd
from pathlib import Path
import streamlit as st
from io import BytesIO

def read_file(input: BytesIO) -> pd.DataFrame:
    try:
        if file_path.name.lower().endswith('.xls','.xlsx'):
            return pd.read_excel(file_path, sheet_name = None)
        return {'Sheet1': pd.read_csv(file_path)}
    except Exception as e:
        print(f'issuing when reading file as {e} from {file_path}')
        return None
    

def de_duplicated(input: pd.DataFrame, unique_column: str) -> pd.DataFrame:
    return input.drop_duplicates(subset = unique_column)

def save_to_excel(input: pd.DataFrame) -> BytesIO:
    output = BytesIO
    with pd.ExcelWriter(output, engine= 'openpyxl')as writer:
        input.to_excel(writer)
    return output

def main():
    st.set_page_config(page_title=  'removal tool', layout= 'wide')
    st.title('removal tool')
    
    st.sidebar.header('upload files')
    input_file = st.sidebar.file_uploader(
        "upload the files which need to combine(csv/excel)",
        type=["csv", 'xls','xlsx'],
        accept_multiple_files= True
    )
    
    input_df = None
    if input_file and len(input_file)>= 2 :
        dataframes = []
        for input in input_file:
            st.subheader(f'processing {input.name}')   
            input_df = read_file(input) 

            if input_df is not None:
                if isinstance(input_df, dict):
                    input_df = list(input_df.values())[0]
                dataframes.append(input_df)
            else:
                st.warning(f'could not read: {input.name}')
        # combine the df
        combined_df = pd.concat(dataframes,ignore_index= True)
        key_column = st.sidebar.selectbox(
            'select the unique column',
            options= combined_df.columns.tolist(),
            help= 'choose the column you want to get unique values'
        )
        result = de_duplicated(combined_df, key_column)
        if result is not None:
            with st.columns(1):
                st.write("the result excel from combination")
                st.dataframe(result)                 
            output = save_to_excel(result)
            st.download_button(
                label= "download the result as excel file",
                data= output.getvalue(),
                file_name= f'{input.name}.xlsx',
            )
if __name__ == "__main__":
    main()

            