from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
from datetime import datetime
from datetime import timezone
from ny_bikes_API import get_agg_data
import traceback
from threading import Thread
import os

# should the main loop run?
run = True

# configure security objects
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# CREATE A STREAM: collection of data that belong to a single session of a single source.
output_stream = output_topic.create_stream("NY-Real-Time-Bikes")
# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "New York Total Bikes Real Time"
# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/NY_Real_Time"


def get_data():

    quix_functions = QuixFunctions(output_stream)

    while run:
        try:
            # Current timestamp
            current_time_i = datetime.now(timezone.utc)

            # ToL API Request
            df_i_agg = get_agg_data()
            total_bikes = df_i_agg.loc[0, 'num_bikes_available'] + df_i_agg.loc[0, 'num_ebikes_available']

            quix_functions.data_handler(current_time_i, total_bikes, df_i_agg)

            # How long did the Request and transformation take
            current_time_j = datetime.now(timezone.utc)
            int_sec = int((current_time_j - current_time_i).seconds)
            print(current_time_i, current_time_j, int_sec, ' bikes: ', total_bikes)

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