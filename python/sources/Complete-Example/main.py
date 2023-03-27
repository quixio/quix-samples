import quixstreams as qx
from quix_functions import QuixFunction
import datetime
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# create the output topic and stream
producer_topic = client.get_topic_producer(os.environ["output"])
stream_producer = producer_topic.create_stream()

# Initialise Quix function
quix_function = QuixFunction(stream_producer)

# Hook up the exception handler callback
stream_producer.on_write_exception = quix_function.on_write_exception_handler

# Update the stream properties
quix_function.set_stream_properties()

# Define your parameters
quix_function.send_parameter_definitions()

# Work with Parameter Data
quix_function.send_parameter_data_epoch()
quix_function.send_parameter_data_specific_date_time()
quix_function.send_parameter_time_delta()

# Work with Events
quix_function.send_event_definitions()
quix_function.send_event_data()

# Close the stream
quix_function.close_stream()

print("Done")
