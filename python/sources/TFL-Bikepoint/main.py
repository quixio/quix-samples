import quixstreams as qx
from quix_functions import QuixFunctions
from datetime import datetime, timezone
import traceback
from tfl_api import get_agg_bikepoint_data
from threading import Thread
import os

# should the main loop run?
run = True

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# CREATE A STREAM
# A stream is a collection of data that belong to a single session of a single source.
# Initiate streams
stream_producer = producer_topic.create_stream("Available-Bikes")

# Give the stream human readable name. This name will appear in data catalogue.
stream_producer.properties.name = "Available Bikes Location"

# Save stream in specific folder in data catalogue to help organize your workspace.
stream_producer.properties.location = "/Bikes"

stream_producer.timeseries.buffer.buffer_timeout = 1000
stream_producer.timeseries.buffer.time_span_in_milliseconds = 1000


def get_data():
    quix_functions = QuixFunctions(stream_producer)

    while run:
        try:
            # Current timestamp
            current_time = datetime.now(timezone.utc)

            # ToL API Request
            df, df_agg = get_agg_bikepoint_data()

            quix_functions.data_handler(df, current_time)

        except Exception:
            print(traceback.format_exc())


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
