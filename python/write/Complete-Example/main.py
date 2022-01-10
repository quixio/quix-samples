from quixstreaming import QuixStreamingClient, StreamEndType, EventLevel
from quix_functions import QuixFunction
import datetime
import os

# Create a client. The client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

# create the output topic and stream
output_topic = client.open_output_topic(os.environ["output"])
output_stream = output_topic.create_stream()

# Initialise Quix function
QuixFunction.__init__(output_stream)

# Hook up the exception handler callback
output_stream.on_write_exception += QuixFunction.on_write_exception_handler

# Update the stream properties
QuixFunction.set_stream_properties()

# Define your parameters
QuixFunction.send_parameter_definitions()

# Work with Parameter Data
QuixFunction.send_parameter_data_epoch()
QuixFunction.send_parameter_data_specific_date_time()
QuixFunction.send_parameter_time_delta()

# Work with Events
QuixFunction.send_event_definitions()
QuixFunction.send_event_data()

# Close the stream
QuixFunction.close_stream()

print("Done")
