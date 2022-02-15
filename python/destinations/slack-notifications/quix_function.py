from quixstreaming import StreamReader, ParameterData
import requests

class QuixFunction:
    def __init__(self, webhook_url, input_stream: StreamReader):
        self.webhook_url = webhook_url
        self.input_stream = input_stream
        self.last_value = False

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        # change the parameter name to whatever you want
        current_value = data.timestamps[0].parameters['HardBraking'].string_value

        # define any logic you need
        if self.last_value != current_value:
            self.last_value = current_value
            
            # send your slack message
            slack_message = {"text": "ALERT:{}".format(current_value)}
            requests.post(self.webhook_url, json=slack_message)
