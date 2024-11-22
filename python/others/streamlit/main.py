import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Streamlit title
st.title("Data Visualization")

# Refresh interval (in seconds)
REFRESH_INTERVAL = 10

# Sample static data
static_data = [
    {"time": "2024-11-01T00:00:00Z", "value": 10},
    {"time": "2024-11-01T01:00:00Z", "value": 15},
    {"time": "2024-11-01T02:00:00Z", "value": 12},
    {"time": "2024-11-01T03:00:00Z", "value": 25},
    {"time": "2024-11-01T04:00:00Z", "value": 20},
]

# Main app loop
while True:
    # Create a DataFrame from static data
    df = pd.DataFrame(static_data)

    # Display waveform plot
    if not df.empty:
        fig = px.line(df, x="time", y="value", title="Waveform")
        st.plotly_chart(fig)

        # Display table
        st.subheader("Data Table")
        st.write(df)
    else:
        st.write("No data available.")

    # Refresh every REFRESH_INTERVAL seconds
    time.sleep(REFRESH_INTERVAL)
    st.rerun()