import threading
import streamlit as st
import time
import threading
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
AVAILABLE_PARAMS = []

# Create a placeholder for the loading spinner
loading_placeholder = st.empty()

placeholder_col1, placeholder_col2 = st.columns(2)
placeholder_raw = None
parameter1 = None
parameter2 = None

def build_dashboard_layout():
    global placeholder_col1, placeholder_col2, placeholder_raw, parameter1, parameter2

    # Create two columns for the select boxes and their headers
    header_col1, header_col2 = st.columns(2)

    with header_col1:
        st.markdown("### Chart 1 Title")
        parameter1 = st.selectbox(
            "Select Parameter 1",
            options=AVAILABLE_PARAMS,
            index=0,
            key="parameter1_select"
        )

    with header_col2:
        st.markdown("### Chart 2 Title")
        parameter2 = st.selectbox(
            "Select Parameter 2",
            options=AVAILABLE_PARAMS,
            index=1,
            key="parameter2_select"
        )

    # Create two columns for the charts
    placeholder_col1, placeholder_col2 = st.columns(2)

    # Initialize placeholders for the charts
    placeholder_col1 = placeholder_col1.empty()  # Placeholder for the first chart
    placeholder_col2 = placeholder_col2.empty()  # Placeholder for the second chart

    # Placeholder for the raw data table below the charts
    placeholder_raw = st.empty()


@st.cache_resource
def queue_init():
    queue = DataQueue()
    queue.start()
    return queue

@st.cache_resource
def data_consumer_init(_queue: DataQueue):
    dc = DataConsumer(_queue)
    thread = threading.Thread(target=dc.start)
    thread.start()
    return dc

# Unique client connection id generated per browser tab.
conid = threading.current_thread().ident

# Blocking queue that exposes Quix data to Streamlit components.
queue = queue_init()

# Data consumer that generates the view model from Quix data for the Streamlit components.
data_consumer = data_consumer_init(queue)

# Event loop to update streamlit components. Try not to copy/modify the dataframes within
# this loop.
while True:

    # Event loop to update streamlit components. Try not to copy/modify the dataframes within
    # this loop.
    if not AVAILABLE_PARAMS:
        # Show loading spinner while waiting for AVAILABLE_PARAMS to be populated
        with loading_placeholder:
            with st.spinner('Waiting for parameters...'):
                while not AVAILABLE_PARAMS:
                    AVAILABLE_PARAMS = data_consumer.get_available_params()
                    time.sleep(0.1)  # Sleep briefly to avoid busy waiting

    # Once AVAILABLE_PARAMS is populated, clear the spinner and build the dashboard layout
    if AVAILABLE_PARAMS and not parameter1 and not parameter2:
        build_dashboard_layout()

    # If parameters are selected, display the charts
    if parameter1 and parameter2:
        df = queue.get(conid)  # Make sure this is non-blocking or handled in a separate thread
        with placeholder_col1:
            st.line_chart(df, x="datetime", y=[parameter1], height=300)
        with placeholder_col2:
            st.line_chart(df, x="datetime", y=[parameter2], height=300)
        with placeholder_raw:
            st.markdown("### Raw Data View")
            st.dataframe(df)