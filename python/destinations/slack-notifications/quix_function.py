from quixstreaming import StreamReader, ParameterData
import requests


class QuixFunction:
    def __init__(self, webhook_url, input_stream: StreamReader):
        self.webhook_url = webhook_url
        self.input_stream = input_stream

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        # change the parameter name to whatever you want
        value = data.timestamps[0].parameters['SlackAlert'].string_value

        # define any logic you need or keep the logic elsewhere

        print("Sending an alert {} {}".format(value, self.webhook_url))

        # send your Slack message
        slack_message = {"text": value}
        requests.post(self.webhook_url, json=slack_message)
