import streamlit as st
import lucatesting as tests
import pandas as pd 

# drag drop for the data file 
file = st.file_uploader('upload and excel file')

# button to submit the file
if st.button("submit"):
    try:
        df = pd.read_excel(file, 0)
        st.session_state["df"] = df
        st.write(df)
        st.success('file read successfully')
    except Exception as e:
        st.error(f'error {e}')

if "df" in st.session_state:
    df = st.session_state['df']
    st.write("Global df:")
    st.write(df)

# test distance matrix button 
# needs different df
# if st.button('check distance matrix'):
#     tests.distance_matrix(df)

# test check consumption during charging button
if st.button('check consumption during charging'):
    try:
        tests.consumption_during_chargin(df)
    except Exception as e:
        print(f'error: {e}')