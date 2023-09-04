import threading
import streamlit as st
import pandas as pd
from data_queue import DataQueue
from data_consumer import DataConsumer

st.set_page_config(
    page_title="Streamlit Dashboard",
    page_icon="favicon.png",
    layout="wide",
)

# Basic changes to the default theme can be done via the .streamlit/config.toml file.
# For custom css update the style.css file 
with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

st.header("Streamlit Dashboard")

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

@st.cache_resource
def queue_init():
    queue = DataQueue()
    queue.start()
    return queue

@st.cache_resource
def data_consumer_init(_queue: DataQueue):
    dc = DataConsumer(_queue)
    dc.start()
    return dc

# Unique client connection id generated per browser tab.
conid = threading.current_thread().ident

# Blocking queue that exposes Quix data to Streamlit components.
queue =  queue_init()

# Data consumer that generates the view model from Quix data for the Streamlit components.
data_consumer = data_consumer_init(queue)

# Event loop to update streamlit components. Try not to copy/modify the dataframes within
# this loop.
while True:
    df = queue.get(conid)
    placeholder_col1.line_chart(df, x="datetime", y=[parameter1])
    placeholder_col2.line_chart(df, x="datetime", y=[parameter2])
    with placeholder_raw.container():
        st.markdown("### Raw Data View")
        st.dataframe(df)