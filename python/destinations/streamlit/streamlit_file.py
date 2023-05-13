import logging
import time

import streamlit as st

from app.conf import (
    STREAMLIT_DATAFRAME_POLL_PERIOD,
)
from app.streamlit_utils import get_stream_df, draw_line_chart_concurrently

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

# Create a placeholder container to fill it with data later
placeholder = st.empty()

while True:
    # Wait for the streaming data to appear on the disk
    df = get_stream_df()
    # The df can be shared between threads and changed over time, so we copy it
    df_copy = df[:]

    with placeholder.container():
        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            # Plot line chart in the first column
            st.markdown("### Chart 1 Title")
            draw_line_chart_concurrently(
                df_copy[["datetime", "Speed", "EngineRPM"]],
                x="datetime",
                y=["Speed", "EngineRPM"],
            )

        with col2:
            # Plot line chart in the second column
            st.markdown("### Chart 2 Title")
            draw_line_chart_concurrently(
                df_copy[["datetime", "Gear", "Brake"]],
                x="datetime",
                y=["Gear", "Brake"],
            )

        # Display the raw dataframe data
        st.markdown("### Raw Data View")
        st.dataframe(df_copy)

    time.sleep(STREAMLIT_DATAFRAME_POLL_PERIOD)
