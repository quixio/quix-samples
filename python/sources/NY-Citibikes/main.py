import quixstreams as qx
from datetime import datetime
from datetime import timezone
from ny_bikes_API import get_agg_data
import traceback
from threading import Thread
import os

# should the main loop run?
run = True

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open the output topic where to write data out
print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# CREATE A STREAM: collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream("NY-Real-Time-Bikes")
# Give the stream human readable name. This name will appear in Live views and Data Explorer.
stream_producer.properties.name = "New York Total Bikes Real Time"
# Save stream in specific folder in data catalogue to help organize your data.
stream_producer.properties.location = "/NY_Real_Time"


def get_data():

    while run:
        try:
            # Current timestamp
            current_time_i = datetime.now(timezone.utc)

            # ToL API Request
            df_i_agg = get_agg_data()
            total_bikes = df_i_agg.loc[0, 'num_bikes_available'] + df_i_agg.loc[0, 'num_ebikes_available']

            # Write bikes data to the output stream
            stream_producer.timeseries.buffer.add_timestamp(current_time_i) \
                .add_value('total_num_bikes_available', total_bikes) \
                .add_value('num_docks_available', df_i_agg.loc[0, 'num_docks_available']) \
                .publish()

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
    thread = Thread(target = get_data)
    thread.start()

    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()