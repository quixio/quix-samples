from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.app import App
from quix_function import QuixFunction
from typing import List
import signal
import threading
import time
import os

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])


# read streams
def read_stream(new_stream: StreamReader):
    print("New Stream read!")

    quix_function = QuixFunction(new_stream)

    # hookup callbacks to handle events
    new_stream.on_stream_closed += quix_function.on_stream_closed_handler
    new_stream.properties.on_changed += quix_function.on_stream_properties_changed_handler
    new_stream.parameters.create_buffer().on_read += quix_function.on_parameter_data_handler
    new_stream.parameters.on_definitions_changed += quix_function.on_parameter_definitions_changed_handler
    new_stream.events.on_definitions_changed += quix_function.on_event_definitions_changed_handler
    new_stream.events.on_read += quix_function.on_event_data_handler


input_topic.on_stream_received += read_stream
input_topic.start_reading()

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()

print("Exiting")
