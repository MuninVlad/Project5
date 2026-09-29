import streamlit as st
import lucatesting as tests
import pandas as pd 

# drag drop for the data file 
file = st.file_uploader('upload bus planning')

# button to submit the file
if st.button("submit bus planning"):
    st.session_state.clear()
    try:
        bp = pd.read_excel(file, 0)
        col_check = tests.check_columnsbp(bp)
        if col_check:
            st.success('file read successfully')
            st.session_state["bp"] = bp
        else:
            st.error('column names dont match')
    except Exception as e:
        st.error(f'error {e}')

if "bp" in st.session_state:
    bp = st.session_state['bp']
    if st.button('show data'):
        st.session_state['show data'] = True
        st.write("Global bus planning:")
        st.write(bp)
        
    if st.button('hide data'):
        st.session_state['show data'] = False
else:
    if st.button('show data'):
        st.session_state['show data'] = False
        st.write("No data")
        
# test distance matrix button 
# needs different df
# if st.button('check distance matrix'):
#     tests.distance_matrix(df)

# test check consumption during charging button
if st.button('check consumption during charging'):
    try:
        invalid = tests.consumption_during_chargin(bp)
        if len(invalid) ==0:
            st.success('no errors detected')
        else:
            st.error(f'invalied consumption during charging {invalid}')
    except Exception as e:
        print(f'error: {e}')


# test trips_with_negative_consumption
if  st.button('check consumption of trips'):
    try:
        enery_test = tests.trips_with_negative_consumption(bp)
        st.success('No errors detected')
    except Exception as e:
        st.error(f'Trips has negative energy consumtion\n{e}')

        # if st.button('click to see more details'):
        #     st.write(f'error: {e}\n\n{enery_test}')


if st.button('test idle with zero minutes'):
    zero_dur = tests.idle_with_zero_minutes(bp)    
    if len(zero_dur) == 0:
        st.success('no idles of zero minutes found')
    else:
        st.error(f'{zero_dur} idles of zero minutes')




### DISTANCE MATRIX TESTS

file = st.file_uploader('upload distance matrix')
# button to submit the file
if st.button("submit distance matrix"):
    try:
        dm = pd.read_excel(file)
        st.session_state["dm"] = dm
        dm_col_check = tests.check_columnsdm(dm)
        if dm_col_check:
            st.success('Successfully read distance matrix')
        else:
            st.error('column names dont match')
    except Exception as e:
        st.error(f'error {e}')

if "dm" in st.session_state:
    dm = st.session_state['dm']

if st.button('Test trips\' time'):
    invalid_times = tests.time_matrix(dm)
    if len(invalid_times) ==0:
        st.success('all trips have valid time')
    else:
        st.error(f'invalid travelling time for {len(invalid_times)} trips')

if st.button('Test travel distance'):
    travel_dist = tests.minus_distance(dm)
    if len(travel_dist) == 0:
        st.success('all trips have valid time')
    else:
        st.error(f'invalid travelling distance for {len(travel_dist)} trips')

