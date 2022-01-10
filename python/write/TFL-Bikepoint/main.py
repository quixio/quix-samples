from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
from datetime import datetime, timezone
import traceback
from tfl_api import get_agg_bikepoint_data
import signal
from threading import Thread, Event
import time

# should the main loop run?
run = True

# configure security objects
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# CREATE A STREAM
# A stream is a collection of data that belong to a single session of a single source.
# Initiate streams
output_stream = output_topic.create_stream("Available-Bikes")

# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "Available Bikes Location"

# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/Bikes"

output_stream.parameters.buffer.buffer_timeout = 1000
output_stream.parameters.buffer.time_span_in_milliseconds = 1000


def get_data():
    QuixFunctions.__init__(output_stream)

    while run:
        try:
            # Current timestamp
            current_time = datetime.now(timezone.utc)

            # ToL API Request
            df, df_agg = get_agg_bikepoint_data()

            QuixFunctions.data_handler(df)

        except Exception:
            print(traceback.format_exc())


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target=get_data)
    thread.start()

    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
