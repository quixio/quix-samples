from quixstreaming import *
import os

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as a parameter.
client = QuixStreamingClient()

# Use Input / Output topics to stream data in or out of your service
input_topic = client.open_input_topic(os.environ["input"])
output_topic = client.open_output_topic(os.environ["output"])

# for more samples, please see library or docs

