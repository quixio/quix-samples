import time

import streamlit as st

from app.conf import (
    STREAMLIT_DATAFRAME_POLL_PERIOD,
)
from app.streamlit_utils import get_stream_df, draw_line_chart_concurrently

# Basic configuration of the Streamlit dashboard
st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

# PARAMETERS SECTION
# Define a list of parameters to show in select widgets.
AVAILABLE_PARAMS = [
    "Steer",
    "Speed",
    "LapDistance",
    "Gear",
    "EngineTemp",
    "EngineRPM",
    "Brake",
]

# DASHBOARD LAYOUT SECTION
# The dashboard layout will consist of 2 columns and one row.
# Each column will have a select widget with available parameters to plot,
# and a chart with the real-time data from Quix, that will be updated in real-time.
# The last row will have a table with raw data.
col1, col2 = st.columns(2)
with col1:
    # Header of the first column
    st.markdown("### Chart 1 Title")
    # Select for the first chart
    parameter1 = st.selectbox(
        label="PARAMETER",
        options=AVAILABLE_PARAMS,
        index=0,
        key="parameter1",
        label_visibility="visible",
    )
    # A placeholder for the first chart to update it later with data
    placeholder_col1 = st.empty()

with col2:
    # Header of the second column
    st.markdown("### Chart 2 Title")
    # Select for the second chart
    parameter2 = st.selectbox(
        label="PARAMETER",
        options=AVAILABLE_PARAMS,
        index=1,
        key="parameter2",
        label_visibility="visible",
    )
    # A placeholder for the second chart to update it later with data
    placeholder_col2 = st.empty()

# A placeholder for the raw data table
placeholder_raw = st.empty()

# REAL-TIME METRICS SECTION
# Below we update the charts with the data we receive from Quix in real time.
# Each 0.5s Streamlit requests new data from Quix and updates the charts.
# Keep the dashboard layout code before "while" loop, otherwise new elements
# will be appended on each iteration.
while True:
    # Wait for the streaming data to become available
    real_time_df = get_stream_df()
    print(f"Receive data from Quix. Total rows: {len(real_time_df)}")
    # The df can be shared between threads and changed over time, so we copy it
    real_time_df_copy = real_time_df[:]

    with placeholder_col1.container():
        # Plot line chart in the first column
        draw_line_chart_concurrently(
            real_time_df_copy,
            # Use "datetime" column for X axis
            x="datetime",
            # Use a column from the first select widget for Y axis
            # You may also plot multiple values
            y=[parameter1],
        )

    # Plot line chart in the second column
    with placeholder_col2.container():
        draw_line_chart_concurrently(
            real_time_df_copy,
            x="datetime",
            # Use a column from the second select widget for Y axis
            y=[parameter2],
        )

    # Display the raw dataframe data
    with placeholder_raw.container():
        st.markdown("### Raw Data View")
        st.dataframe(real_time_df_copy)

    # Wait for 0.5s before asking for new data from Quix
    time.sleep(STREAMLIT_DATAFRAME_POLL_PERIOD)
