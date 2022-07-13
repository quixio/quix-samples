from quixstreaming import QuixStreamingClient, StreamReader, AutoOffsetReset
from quixstreaming.app import App

from quixstreaming import Logging, LogLevel
Logging.update_factory(LogLevel.Debug)

import threading as thread
import os

import time  # to simulate a real time data, time loop

import pandas as pd  # read csv, df manipulation
import streamlit as st  # 🎈 data web app development
from streamlit.scriptrunner.script_run_context import add_script_run_ctx

client = QuixStreamingClient()

input_topic = client.open_input_topic(os.environ["input"], None, auto_offset_reset=AutoOffsetReset.Latest)

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

# data frame for the data
df = pd.DataFrame()
# creating a single-element container
placeholder = st.empty()

# callback called for each incoming data frame
def on_read_pandas_data(df_i: pd.DataFrame):
    global df

    # format the datetime
    df_i['datetime'] = pd.to_datetime(df_i['time'])

    # append the new data
    df = df.append(df_i)
    # keep the last 500 data points
    df = df.iloc[-500:, :]

# callback called for each incoming stream
def read_stream(input_stream: StreamReader):        
    # React to new data received from input topic.
    input_stream.parameters.on_read_pandas += on_read_pandas_data

# hook up the read_stream callback
input_topic.on_stream_received += read_stream

# a flag to allow us to stop the main thread on shut down
run_thread = True

# when shutdown is started, set the flag to false
def shutdown():
    global run_thread
    run_thread = False

def update_dashboard():
    global df
    
    # use the in memory dataframe to refresh the dashboard
    while run_thread:

        local_df = df.copy(deep=True)  # copy reference, so df can be changed outside of this loop while we're working on it

        # show the spinner while we wait for data
        with st.spinner('Loading data..'):
            while local_df is None or "Speed" not in local_df.columns:
                time.sleep(0.2) # wait a moment for more data to arrive
                local_df = df.copy(deep=True)  # copy reference, so df can be changed outside of this loop while we're working on it

        with placeholder.container():
            fig_col1, fig_col2 = st.columns(2)
            with fig_col1:
                st.markdown("### Chart 1 Title")
                st.line_chart(local_df[["datetime", 'Speed', 'EngineRPM']].set_index("datetime"))

            with fig_col2:
                st.markdown("### Chart 2 Title")
                st.line_chart(local_df[["datetime", 'Gear', 'Brake']].set_index("datetime"))

            # display the raw data from the buffer
            st.markdown("### Raw Data View")
            st.dataframe(local_df)

        # take a nap
        time.sleep(0.1)

# setup the thread to update the ui
ui_updater_thread = thread.Thread(target=update_dashboard)
add_script_run_ctx(ui_updater_thread)
ui_updater_thread.start()

# run the app, open the topic, listen for shutdown events
App.run(before_shutdown=shutdown)
