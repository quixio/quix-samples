from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from functions import Functions
from datetime import datetime
import os
import threading

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# Create a new output_stream. A stream is a collection of data that belong to a single session of a single source.
# For example single car journey.
# If you don't specify a stream id, a random guid is used.
output_stream = output_topic.create_stream()

# If you want to append data into the stream later, assign a stream id.
# stream = output_topic.create_stream("my-own-stream-id")

output_stream.properties.name = "Motor Data - {}".format(datetime.utcnow().strftime("%d-%m-%Y %X"))
output_stream.properties.location = "/motor data"
output_stream.parameters.buffer.packet_size = 1

functions = Functions(output_stream)

# start a thread to write the data
thread = threading.Thread(target=functions.write_data)
thread.start()


def before_shutdown():
    # before exiting, stop the main loop
    functions.stop_loop()


App.run(before_shutdown=before_shutdown)

# wait for worker thread to end
thread.join()

print("Exiting")
