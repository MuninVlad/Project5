import streamlit as st
import pandas as pd
import plotly.express as px


import lucatesting as t

st.set_page_config(
    page_title="Transdev Bus Planning Tool",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Transdev Eindhoven: Bus Plan Verification & Optimization Tool")
st.markdown("Software tool for checking schedule feasibility and KPIs for bus lines 400 and 401.")


col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📁 Upload Data")
    uploaded_file = st.file_uploader("Upload Bus Planning Excel File", type=["xlsx"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully!")
        st.write("Preview of data:")
        st.dataframe(df.head(5), use_container_width=True)

    else:
        st.info("Please upload your Excel file to begin.")

with col2:
    st.subheader('Actions and Controls')

    if st.button("🔍 Check for errors", use_container_width=True):
        if uploaded_file is not None:
            successcount = 0
            #Test 1
            coltest = t.check_columnsbp(df)
            if coltest:
                st.success("All required columns are present!")
                successcount = successcount+1
            else:
                st.error("Missing required columns in the dataset.")

            #Test 2
            chargingtest = t.consumption_during_chargin(df)
            if chargingtest.empty:
                st.success("✅ All charging activities are correct.")
                successcount = successcount+1
            else:
                st.error(f"❌ Found {len(chargingtest)} invalid charging activities (consumption >= 0):")
                st.dataframe(chargingtest, use_container_width=True)


            #Test 3
            invalid_trips_df = t.trips_with_negative_consumption(df)
            if invalid_trips_df.empty:
                st.success("✅ All trips have correct positive consumption.")
                successcount = successcount+1
            else:
                st.error(f"❌ Found {len(invalid_trips_df)} service/material trips with negative consumption:")
                st.dataframe(invalid_trips_df, use_container_width=True)

            #Test 4
            zero_idle_df = t.idle_with_zero_minutes(df)
            if zero_idle_df.empty:
                st.success("✅ No idle times with zero minutes found.")
                successcount = successcount+1
            else:
                st.warning(f" Found {len(zero_idle_df)} idle activities with 0 duration:")
                st.dataframe(zero_idle_df, use_container_width=True)


            if successcount == 4:
                st.success("✅ No errors in the data")

        else:
            st.error("Please upload a file first!")

    
    
    

st.subheader("Improve bus planning")

if st.button("🚀 Improve this bus planning", use_container_width=True):
        if uploaded_file is not None:
            # optimization algorithm here
            st.info("🔄 Running optimization algorithm...")
        else:
            st.error("Please upload a file first!")


st.markdown("📥 Export Result")
    
st.download_button(
        label="Download Improved Bus Plan (.xlsx)",
        data=b"placeholder_data",  # final dataframe converted to bytes later
        file_name="improved_bus_planning.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.subheader("📊 Number of buses")

