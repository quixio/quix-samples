from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from conversion_functions import ConversionFunctions
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

print("Opening input and output topics")

# Change consumer group to a different constant if you want to run model locally.
# Open the RAW input topic.
input_topic = client.open_raw_input_topic(os.environ["input"], "conversion-consumer-group")
output_topic = client.open_output_topic(os.environ["output"])

conversion_functions = ConversionFunctions(output_topic)

# Hook up events before initiating read to avoid losing out on any data
input_topic.on_message_read += conversion_functions.raw_message_handler

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()
