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

# Basic changes to the default theme can be done via the .streamlit/config.toml file. For custom css
# update the style.css file 
with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

st.header("Streamlit Dashboard")

col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
with col1:
    parameter1 = st.selectbox(
        label="PARAMETER",
        options=["LapNumber"],
        index=0,
        key="parameter1",
        label_visibility="hidden",
    )
    col1_row1 = st.empty()

with col2:
    parameter2 = st.selectbox(
        label="PARAMETER",
        options=["Speed"],
        index=0,
        key="parameter2",
        label_visibility="hidden",
    )
    col2_row1 = st.empty()

with col3:
    parameter3 = st.selectbox(
        label="PARAMETER",
        options=["EngineTemp"],
        index=0,
        key="parameter3",
        label_visibility="hidden",
    )
    col3_row1 = st.empty()

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

conid = threading.current_thread().ident
queue =  queue_init()
data_consumer = data_consumer_init(queue)

while True:
    data = queue.get(conid)
    if "f1_telemetry" in data:
        df = data["f1_telemetry"]
        if parameter1 in df and not pd.isna(df[parameter1].iloc[-1]):
            col1_row1.metric(label="label1", value=round(df[parameter2].iloc[-1], 1), label_visibility="hidden")
        if parameter2 in df and not pd.isna(df[parameter2].iloc[-1]):
            col2_row1.metric(label="label2", value=round(df[parameter3].iloc[-1], 1), label_visibility="hidden")
        if parameter3 in df and not pd.isna(df[parameter3].iloc[-1]):
            col3_row1.metric(label="label3", value=int(df[parameter3].iloc[-1]), label_visibility="hidden")