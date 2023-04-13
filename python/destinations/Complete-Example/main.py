import quixstreams as qx
from quix_function import QuixFunction
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"])


# read streams
def read_stream(new_stream: qx.StreamConsumer):
    print("New Stream read!")

    quix_function = QuixFunction(new_stream)

    # hookup callbacks to handle events
    new_stream.on_stream_closed = quix_function.on_stream_closed_handler
    new_stream.properties.on_changed = quix_function.on_stream_properties_changed_handler
    new_stream.timeseries.create_buffer().on_data_released = quix_function.on_data_handler
    new_stream.timeseries.on_definitions_changed = quix_function.on_parameter_definitions_changed_handler
    new_stream.events.on_definitions_changed = quix_function.on_event_definitions_changed_handler
    new_stream.events.on_data_received = quix_function.on_event_data_handler


consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
qx.App.run()

print("Exiting")
