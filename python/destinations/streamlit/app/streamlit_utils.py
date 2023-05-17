import io
import logging
import threading
import time
import urllib.request
from typing import Union, Sequence

import pandas as pd
import streamlit as st

from app.conf import (
    STREAMLIT_DATAFRAME_POLL_PERIOD,
    STREAMLIT_DATAFRAME_POLL_TIMEOUT,
    STREAMLIT_DATAFRAME_REQUEST_URL,
    STREAMLIT_DATAFRAME_REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)

__all__ = ("get_stream_df", "draw_line_chart_concurrently")


def _read_df_from_url(url: str, timeout: int):
    logger.debug(f"Read dataframe from url url={url}")
    response = urllib.request.urlopen(url, timeout=timeout)
    with io.BytesIO(response.read()) as f:
        df = pd.read_csv(f)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df


@st.cache_resource(
    ttl=STREAMLIT_DATAFRAME_POLL_PERIOD,
    show_spinner="Waiting for the streaming data...",
)
def get_stream_df(
    url: str = STREAMLIT_DATAFRAME_REQUEST_URL,
    request_timeout: int = STREAMLIT_DATAFRAME_REQUEST_TIMEOUT,
    poll_period: float = STREAMLIT_DATAFRAME_POLL_PERIOD,
    poll_timeout: float = STREAMLIT_DATAFRAME_POLL_TIMEOUT,
) -> pd.DataFrame:
    """
    Read DataFrame data from `url` in a loop.
    The result is cached by Streamlit process and is shared between sessions
    to reduce memory usage.

    :param url: URL to poll for DataFrame. Default - http://localhost:8000
    :param request_timeout: Request timeout for DataFrame requests
    :param poll_period: How often to request DataFrame data in seconds
    :param poll_timeout: How many seconds to wait for the file before raising the error
    :return: DataFrame with data from Quix
    """

    start_time = time.monotonic()
    while True:
        try:
            return _read_df_from_url(url=url, timeout=request_timeout)
        except OSError:
            logger.info(f'Dataframe url "{url}" is not found')
        except pd.errors.EmptyDataError:
            logger.info(f"Dataframe is empty")

        # If timeout exceeded, raise the error
        if time.monotonic() - start_time >= poll_timeout:
            raise TimeoutError(f"Could not find dataframe file in {poll_timeout}s")

        logger.info(f'Wait {poll_period}s for the dataframe url "{url}"')
        time.sleep(poll_period)
        continue


@st.cache_resource
def _get_render_lock() -> threading.Lock:
    """
    A shared lock used to prevent charts from rendering concurrently.
    """

    return threading.Lock()


def draw_line_chart_concurrently(
    data: pd.DataFrame,
    *,
    x: Union[str, None] = None,
    y: Union[str, Sequence[str], None] = None,
):
    """
    Draw line chart in a locking fashion.
    Otherwise, streamlit.line_chart occasionally fails with
    "RuntimeError: dictionary changed size during iteration"
    """

    with _get_render_lock():
        st.line_chart(data, x=x, y=y)
