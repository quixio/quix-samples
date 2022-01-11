from quixstreaming import ParameterData, EventData
from twilio.rest import Client

import os


class TwilioSink:

    def __init__(self):
        self._time = None

        # Connection to Twilio account
        account_sid = "{placeholder:account_sid}"
        auth_token = "{placeholder:auth_token}"
        self._twilio_client = Client(account_sid, auth_token)

        self._messaging_service_sid = "{placeholder:messaging_service_sid}"

        self._phone_numbers = os.environ["numbers"].split(",")

        self._message_limit_per_minute = 2  # Limit of how many messages per minute we allow to send.
        self._messages_sent = []  # Epochs of messages sent.

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        print(data)
        self._send_text_message(str(data))

    # Callback triggered for each new event data.
    def on_event_data_handler(self, data: EventData):
        print(data)
        self._send_text_message(str(data))

    # Send message using Twilio
    def _send_text_message(self, body):
        # Filter messages older than 60s to keep last minute buffer.
        self._messages_sent = list(
            filter(lambda x: x > self._time.time() - 60, self._messages_sent))

        # If we have not reached the limit, we proceed with sending
        if len(self._messages_sent) < self._message_limit_per_minute:
            for phone_number in self._phone_numbers:
                message = self._twilio_client.messages.create(
                    messaging_service_sid=self._messaging_service_sid,
                    body=body,
                    to=phone_number
                )

                print("Message {0} sent to {1}".format(body, phone_number))
                self._messages_sent.append(self._time.time())
        else:
            print("Message {0} skipped due to message limit reached.".format(body))
