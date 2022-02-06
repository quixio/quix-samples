from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.app import App
from quix_function import QuixFunction
import os

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as a parameter.
client = QuixStreamingClient('{placeholder:sdktoken}')

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

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()

print("Exiting")
