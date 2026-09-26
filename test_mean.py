from lucatesting import distance_matrix
import streamlit as st
import pandas as pd 

# drag drop for the data file 
file = st.file_uploader('upload and excel file')

# button to submit the file
if st.button("submit"):
    try:
        df = pd.read_excel(file, 0)
        st.write(df)
        st.success('file read successfully')
    except:
        st.error('error')

# a button to start the test 
if st.button('check distance matrix'):
    distance_matrix(df)

if st.button('check ')
    
