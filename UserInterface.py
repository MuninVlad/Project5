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