from quixstreaming import *

# Quix streaming client takes credentials from the online IDE but you can always pass an SDK token manually as a parameter.
client = QuixStreamingClient('{placeholder:token}')

# Use Input / Output topics to stream data in or out of your service
input_topic = client.open_input_topic('THE_TOPIC_ID_TO_READ_FROM')
output_topic = client.open_output_topic('THE_TOPIC_ID_TO_WRITE_TO')

# for more samples, please see library or docs

