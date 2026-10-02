import streamlit as st
import pandas as pd
import plotly.express as px


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
            st.warning("Checking file for consistency and feasibility errors")
            # function for testing
        else:
            st.error("Please upload a file first!")

    if st.button("🚀 Improve this bus planning", use_container_width=True):
        if uploaded_file is not None:
            # optimization algorithm here
            st.info("🔄 Running optimization algorithm... (Backend pending)")
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
