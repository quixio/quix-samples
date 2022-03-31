from quixstreaming import InputTopic, StreamReader, ParameterData, EventData, OutputTopic
from quixstreaming import LocalFileStorage
import os
import pickle


class StatefullProcessing:
    def __init__(self, input_topic: InputTopic, input_stream: StreamReader, output_topic: OutputTopic):
        self.input_stream = input_stream
        self.output_topic = output_topic

        self.state = None

        self.storage_key = os.environ["storage_version"]

        self.storage = LocalFileStorage(os.environ["storage_version"])

        input_topic.on_committed += self.save_state

        if self.storage.containsKey(self.storage_key):
            print("State loaded.")
            self.state = self.load_state()
        else:
            print("No state found, initializing state.")
            self.init_state()

    def init_state(self):
        return

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def load_state(self):
        return pickle.loads(self.storage.get(self.storage_key))

    def save_state(self):
        print("State saved.")
        if self.state is not None:
            self.storage.set("dashboard", pickle.dumps(self.state))

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        return

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        return


        