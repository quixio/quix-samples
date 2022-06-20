from quixstreaming import StreamReader, ParameterData, EventData
import requests
import pandas as pd

class QuixFunction:
    def __init__(self, webhook_url, input_stream: StreamReader):
        self.webhook_url = webhook_url
        self.input_stream = input_stream

        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df: pd.DataFrame):

        print(str(df))

        # send your slack message
        slack_message = {"text": str(df)}
        requests.post(self.webhook_url, json=slack_message)

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

        # send your slack message
        slack_message = {"text": str(data)}
        requests.post(self.webhook_url, json=slack_message)