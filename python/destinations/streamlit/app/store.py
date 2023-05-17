import io
import threading

import pandas as pd

__all__ = ("StreamStateStore",)


class StreamStateStore:
    """
    Store that keeps last N rows of pd.DataFrame in memory and
    saves them to the disk
    """

    def __init__(self, max_size: int = 500):
        """
        Initialize the store

        :param max_size: number of the most recent rows to keep
        """
        self._df = pd.DataFrame()
        self._max_size = max_size
        self._lock = threading.Lock()

    def append(self, new_df: pd.DataFrame):
        """
        Add new rows to the dataframe and delete the old ones

        :param new_df: pd.DataFrame with new data
        """
        with self._lock:
            self._df = pd.concat([self._df, new_df])
            self._df = self._df.iloc[-self._max_size :, :]

    def to_csv_bytes(self) -> bytes:
        """
        Serialize the store state to CSV
        """
        with self._lock, io.BytesIO() as f:
            self._df.to_csv(f, index=False)
            f.seek(0)
            return f.read()
