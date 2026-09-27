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
        col_check = tests.check_columns(df)
        if col_check:
            st.success('file read successfully')
        else:
            st.error('column names dont match')
    except Exception as e:
        st.error(f'error {e}')

if "df" in st.session_state:
    df = st.session_state['df']
    if st.button('show data'):
        st.session_state['show data'] = True
        st.write("Global df:")
        st.write(df)
        
    if st.button('hide data'):
        st.session_state['show data'] = False

# test distance matrix button 
# needs different df
# if st.button('check distance matrix'):
#     tests.distance_matrix(df)

# test check consumption during charging button
if st.button('check consumption during charging'):
    try:
        invalid = tests.consumption_during_chargin(df)
        if len(invalid) ==0:
            st.success('no errors detected')
        else:
            st.error(f'invalied consumption during charging {invalid}')
    except Exception as e:
        print(f'error: {e}')


# test trips_with_negative_consumption
if  st.button('check consumption of trips'):
    try:
        enery_test = tests.trips_with_negative_consumption(df)
        st.success('No errors detected')
    except Exception as e:
        st.error(f'Trips has negative energy consumtion\n{e}')

        # if st.button('click to see more details'):
        #     st.write(f'error: {e}\n\n{enery_test}')


if st.button('test idle with zero minutes'):
    zero_dur = tests.idle_with_zero_minutes(df)    
    if len(zero_dur) == 0:
        st.success('no idles of zero minutes found')
    else:
        st.error(f'{zero_dur} idles of zero minutes')
