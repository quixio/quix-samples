from quixstreaming import InputTopic, StreamReader, ParameterData, EventData
from quixstreaming import LocalFileStorage
import os
import pickle

class CrossStreamStatefullProcessing:

    def __init__(self, input_topic: InputTopic):
        self.input_topic = input_topic

        self.state = None

        self.storage_key = "dashboard"

        input_topic.on_stream_received += self.read_stream

        self.storage = LocalFileStorage(os.environ["storage_version"])

        input_topic.on_committed += self.save_state

        if self.storage.containsKey(self.storage_key):
            print("State loaded.")
            self.state = self.load_state()
        else:
            print("No state found, initializing state.")
            self.init_state()
        

        print("Listening to streams. Press CTRL-C to exit.")

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

    def start(self):
        self.input_topic.start_reading()


    def read_stream(self, input_stream: StreamReader):
        print("New stream read:" + input_stream.stream_id)
        input_stream.parameters.on_read += self.on_parameter_data_handler


    def on_parameter_data_handler(self, data: ParameterData):
        return
   
    def on_event_data_handler(self, data: EventData):
        return
        
