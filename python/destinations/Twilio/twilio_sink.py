import quixstreams as qx
from twilio.rest import Client
import time
import os
import pandas as pd

class TwilioSink:

    def __init__(self):
        self._time = time.time()

        # Connection to Twilio account
        account_sid = os.environ["account_sid"]
        auth_token = os.environ["auth_token"]
        self._twilio_client = Client(account_sid, auth_token)

        self._messaging_service_sid = os.environ["messaging_service_sid"]

        self._phone_numbers = os.environ["numbers"].split(",")

        self._message_limit_per_minute = int(os.environ["message_limit"])  # Limit of how many messages per minute we allow to send.
        self._messages_sent = []  # Epochs of messages sent.

    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        print(df)
        self._send_text_message(str(df))

    # Callback triggered for each new event data.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data)
        self._send_text_message(data.value)

    # Send message using Twilio
    def _send_text_message(self, body):
        # Filter timestamps older than 60s to keep last minute timestamps.
        self._messages_sent = list(
            filter(lambda x: x > self._time - 60, self._messages_sent))

        # If we have not reached the limit, we proceed with sending
        if len(self._messages_sent) < self._message_limit_per_minute:
            for phone_number in self._phone_numbers:
                message = self._twilio_client.messages.create(
                    messaging_service_sid = self._messaging_service_sid,
                    body = body,
                    to = phone_number
                )

                print("Message {0} sent to {1}".format(body, phone_number))
                self._time = time.time()
                self._messages_sent.append(self._time)

        else:
            print("Message {0} skipped due to message limit reached.".format(body))
