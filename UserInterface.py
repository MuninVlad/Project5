import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Transdev Bus Planning Tool",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Transdev Eindhoven: Bus Plan Verification & Optimization Tool")
st.markdown("Prototype software tool for checking schedule feasibility and KPIs for bus lines 400 and 401.")


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