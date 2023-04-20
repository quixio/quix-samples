import quixstreams as qx
from functions import Functions
from datetime import datetime
import os
import threading

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open the output topic
print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# Create a new stream_producer. A stream is a collection of data that belong to a single session of a single source.
# For example single car journey.
# If you don't specify a stream id, a random guid is used.
stream_producer = producer_topic.create_stream()

# If you want to append data into the stream later, assign a stream id.
# stream = producer_topic.create_stream("my-own-stream-id")

stream_producer.properties.name = "Currency Data - {}".format(datetime.utcnow().strftime("%d-%m-%Y %X"))
stream_producer.properties.location = "/currency data"
stream_producer.timeseries.buffer.packet_size = 1

functions = Functions(stream_producer)

# start a thread to write the data
thread = threading.Thread(target = functions.publish_data)
thread.start()


def before_shutdown():
    # before exiting, stop the main loop
    functions.stop_loop()


qx.App.run(before_shutdown = before_shutdown)

# wait for worker thread to end
thread.join()

print("Exiting")
