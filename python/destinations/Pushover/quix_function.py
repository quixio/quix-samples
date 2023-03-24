import quixstreams as qx
import requests
import pandas as pd
import os


class QuixFunction:

    def __init__(self, stream_consumer: qx.StreamConsumer):
        # Credentials
        self.apitoken = os.environ["api_token"]
        self.userkey = os.environ["user_key"]
        self.baseurl = os.environ["base_url"]
        # self.stream_consumer = stream_consumer

        # set the format for printing pandas data
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

    # Callback triggered for each new parameter data
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):

        print(str(df))

        # send your push message
        try:
            pushmsg = {'token': self.apitoken,
                       'user': self.userkey,
                       'message': 'Threshold has been crossed'}
            requests.post(self.baseurl, json = pushmsg)

        except Exception as e:
            print(f"Error connecting to push API: {e}")

    # Callback triggered for each new event
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data)

        # send your push message
        try:
            requests.get(self.url)
        except Exception as e:
            print(f"Error connecting to push API: {e}")
