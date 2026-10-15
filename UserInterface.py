import streamlit as st
import pandas as pd
import plotly.express as px
import io

import lucatesting as t
import Algorithm as a



st.set_page_config(
    page_title="Transdev Bus Planning Tool",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Transdev Eindhoven: Bus Plan Verification & Optimization Tool")
st.markdown("Software tool for checking schedule feasibility and KPIs for bus lines 400 and 401.")

if "total_buses" not in st.session_state:
    st.session_state.total_buses = 0

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📁 Upload Data")
    uploaded_main = st.file_uploader("1. Upload Bus Plan OR Timetable (.xlsx)", type=["xlsx"])
    uploaded_distance = st.file_uploader("2. Upload Distance Matrix (Optional)", type=["xlsx"])
    
    if uploaded_main is not None:
        df = pd.read_excel(uploaded_main)
        
        if 'activity' in df.columns:
            st.success("✅ Bus Plan detected and uploaded successfully!")
        else:
            st.success("✅ Timetable detected and uploaded successfully!")
            
        dm_source = uploaded_distance if uploaded_distance is not None else 'DistanceMatrix.xlsx'
        if uploaded_distance is not None:
            st.info("Using custom uploaded Distance Matrix.")
        else:
            st.info("Using default local DistanceMatrix.xlsx.")
            
        st.write("Preview of data:")
        st.dataframe(df.head(5), use_container_width=True)
    else:
        st.info("Please upload a Bus Plan or Timetable to begin.")
    

with col2:
    st.subheader('Error checking')

    if st.button("🔍 Check for errors", use_container_width=True):
        if uploaded_main is not None:
            df = pd.read_excel(uploaded_main)

            if 'activity' not in df.columns or 'energy consumption' not in df.columns:
                st.warning("⚠️ This file is a raw Timetable. Error checking is designed for completed Bus Plans. Please scroll down to 'Improve bus planning' to generate a plan.")
            
            # 2. THE TESTS (Must be indented under the 'else:')
            else:
                successcount = 0
            
             #Test 1
                coltest = t.check_columnsbp(df)
                if coltest:
                    #st.success("All required columns are present!")
                    successcount = successcount+1
                else:
                    st.error("Missing required columns in the dataset.")

                #Test 2
                chargingtest = t.consumption_during_chargin(df)
                if chargingtest.empty:
                    #st.success("✅ All charging activities are correct.")
                    successcount = successcount+1
                else:
                    st.error(f"❌ Found {len(chargingtest)} invalid charging activities (consumption >= 0):")
                    st.dataframe(chargingtest, use_container_width=True)


                #Test 3
                invalid_trips_df = t.trips_with_negative_consumption(df)
                if invalid_trips_df.empty:
                    #st.success("✅ All trips have correct positive consumption.")
                    successcount = successcount+1
                else:
                    st.error(f"❌ Found {len(invalid_trips_df)} service/material trips with negative consumption:")
                    st.dataframe(invalid_trips_df, use_container_width=True)


                #Test 4
                try:
                    dm_df = pd.read_excel('DistanceMatrix.xlsx')
                    neg_distance_idx = t.minus_distance(dm_df)
                except FileNotFoundError:
                    st.error("⚠️ Could not find 'DistanceMatrix.xlsx' in the project folder.")
                if len(neg_distance_idx) == 0:
                    successcount += 1
                else:
                    st.error(f"❌ Found {len(neg_distance_idx)} records with negative distances:")
                    st.dataframe(df.loc[neg_distance_idx], use_container_width=True)

                #Test 5
                error_dest_trips = t.trip_with_the_same_start_and_end(df)
                if error_dest_trips.empty:
                    successcount += 1
                else:
                    st.error(f"❌ Found {len(error_dest_trips)} trips where the start and end locations are the same:")
                    st.dataframe(error_dest_trips, use_container_width=True)

                # Test 6: Check for nulls (excluding the 'line' column)
                num_of_nulls = t.check_nulls(df)
                if num_of_nulls == 0:
                    successcount += 1
                else:
                    st.error(f"❌ Found {num_of_nulls} missing/null values in the dataset (excluding 'line' column).")

                # Test 7
                num_duplicates = t.check_duplicates(df)
                if num_duplicates == 0:
                    successcount += 1
                else:
                    st.error(f"❌ Found {num_duplicates} duplicate rows in the dataset.")        

                # Test 8 
                invalid_times = t.invalid_trip_time(df)
                if len(invalid_times) ==0:
                    successcount += 1
                else:
                    st.error(f'❌ Found {len(invalid_times)} invalid planned times {st.dataframe(invalid_times)}')                
                    # st.error(f'invalid travelling time for {len(invalid_times)} trips\n{invalid_times}')

                if successcount == 8:
                    st.success("✅ No errors in the data!")

        else:
            st.error("Please upload a file first!")






st.subheader("⚙️ Parameters")
p1, p2, p3 = st.columns(3)
with p1:
    energy_per_km = st.number_input("Energy consumption per km (kWh/km)", min_value=0.7, value=1.2,  max_value=2.5)
with p2:
    buffer_min = st.number_input("Buffer (minutes)", value=0, step=1)
with p3:
    soh = st.number_input("State of Health", value=0.85, max_value=0.95)

st.subheader("Improve bus planning")

if st.button("🚀 Improve bus planning", use_container_width=True):
        if uploaded_main is not None:


            
            with st.spinner("🔄 Running optimization algorithm..."):

                timetable_df = pd.read_excel(uploaded_main)
                distance_df = pd.read_excel(uploaded_distance)
            

                lookup = a.make_distance_lookup('DistanceMatrix.xlsx')
                usable, lowest, highest, start_charge = a.battery_limits(300, 0.85)
                trips = a.load_trips(uploaded_main, 'DistanceMatrix.xlsx')
            
                buses, number_of_buses = a.build_plan(trips, lookup, lowest, highest, start_charge)
            

                st.session_state.optimized_df = a.convert_plan_to_dataframe(buses)
                st.session_state.total_buses = number_of_buses

        else:
            st.error("Please upload a file first!")



if st.session_state.get("optimized_df") is not None:
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.optimized_df.to_excel(writer, index=False, sheet_name='Improved_Plan')
    excel_data = output.getvalue()

    st.divider()

    st.subheader("📋 Optimized Bus Plan Preview")
    st.dataframe(st.session_state.optimized_df.head(), use_container_width=True)

    st.divider()

    st.subheader("📊 Number of buses")
    st.metric(label="Total Buses Required", value=st.session_state.total_buses)

    st.divider()

 #   --- GANTT CHART ---
    st.subheader("📅 Schedule Gantt Chart")
    
    gantt_df = st.session_state.optimized_df.copy()
    
    # 1. Sort buses numerically (Bus 1, Bus 2, Bus 3...)
    gantt_df['bus_num'] = pd.to_numeric(gantt_df['bus'])
    gantt_df = gantt_df.sort_values(by=['bus_num', 'start time'])
    gantt_df['bus_label'] = "Bus " + gantt_df['bus_num'].astype(str)
    
    # 2. Format datetimes for Plotly timeline
    dummy_date = "2026-01-01 "
    gantt_df['start_dt'] = pd.to_datetime(dummy_date + gantt_df['start time'].astype(str))
    gantt_df['end_dt'] = pd.to_datetime(dummy_date + gantt_df['end time'].astype(str))
    gantt_df.loc[gantt_df['end_dt'] < gantt_df['start_dt'], 'end_dt'] += pd.Timedelta(days=1)
    
    # Calculate exact duration in minutes
    gantt_df['duration_mins'] = ((gantt_df['end_dt'] - gantt_df['start_dt']).dt.total_seconds() / 60).astype(int)

    # 3. Filter out 0-minute idle events so tiny gaps don't trigger false hovers
    gantt_df = gantt_df[~((gantt_df['activity'] == 'idle') & (gantt_df['duration_mins'] <= 0))].copy()

    # 4. Create short text labels to display inside the bars
    def make_label(row):
        if row['activity'] == 'service trip' and pd.notna(row['line']):
            return f"L{int(row['line'])}"
        elif row['activity'] == 'charging':
            return f"⚡ {row['duration_mins']}m"
        elif row['duration_mins'] >= 10:
            return f"{row['duration_mins']}m"
        return ""

    gantt_df['label_text'] = gantt_df.apply(make_label, axis=1)

    # 5. Calculate dynamic height for thicker rows (45px per bus)
    num_buses = gantt_df['bus_num'].nunique()
    chart_height = max(400, num_buses * 45)

# 6. Build Gantt Chart (Using hover_data passes columns safely to customdata for traces)
    fig_gantt = px.timeline(
        gantt_df,
        x_start="start_dt",
        x_end="end_dt",
        y="bus_label",
        color="activity",
        text="label_text",
        title="Bus Activity Timeline",
        labels={"bus_label": "Bus", "activity": "Activity Type"},
        hover_data=["activity", "line", "start location", "end location", "start time", "end time", "duration_mins", "energy consumption"],
        color_discrete_map={
            "service trip": "#1f77b4",   # Blue
            "material trip": "#ff7f0e",  # Orange
            "charging": "#2ca02c",       # Green
            "idle": "#7f7f7f"            # Gray
        }
    )

    # 7. Axis formatting
    fig_gantt.update_yaxes(
        autorange="reversed", 
        title_text="Bus Number"
    )
    
    fig_gantt.update_xaxes(
        tickformat="%H:%M",
        dtick=1800000,        # Vertical gridlines every 30 minutes
        showgrid=True,
        gridcolor="#333333",
        gridwidth=1,
        title_text="Time (HH:MM)"
    )

    # 8. Configure hover card template using indices from hover_data
    fig_gantt.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        marker_line_color="black",
        marker_line_width=1,
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "<b>Activity:</b> %{customdata[0]}<br>" +
            "<b>Line:</b> %{customdata[1]}<br>" +
            "<b>Route:</b> %{customdata[2]} ➔ %{customdata[3]}<br>" +
            "<b>Time:</b> %{customdata[4]} - %{customdata[5]} (%{customdata[6]} mins)<br>" +
            "<b>Energy:</b> %{customdata[7]:.2f} kWh<extra></extra>"
        )
    )

    # 9. Layout settings
    fig_gantt.update_layout(
        height=chart_height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_gantt, use_container_width=True)




    st.divider()

    st.markdown("📥 Export Result")
    st.download_button(
        label="Download Improved Bus Plan (.xlsx)",
        data=excel_data,
        file_name="improved_bus_planning.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.divider()




