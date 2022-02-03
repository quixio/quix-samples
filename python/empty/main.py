from quixstreaming import *
import os

# Quix streaming client takes credentials from the online IDE but you can always pass an SDK token manually as a parameter.
client = QuixStreamingClient('{placeholder:token}')

# Use Input / Output topics to stream data in or out of your service
input_topic = client.open_input_topic(os.environ["input"])
output_topic = client.open_output_topic(os.environ["output"])

# for more samples, please see library or docs

