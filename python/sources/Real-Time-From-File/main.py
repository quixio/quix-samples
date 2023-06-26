import quixstreams as qx
import pandas as pd
import time
import os
from threading import Thread

# should the main loop run?
run = True

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# CREATE A NEW STREAM
# A stream is a collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream()
# EDIT STREAM
# stream = producer_topic.create_stream("my-own-stream-id")  # To append data into the stream later, assign a stream id.
stream_producer.properties.name = "ExampleData"  # Give the stream a human readable name (for the data catalogue).
stream_producer.properties.location = "/example data"  # Save stream in specific folder to organize your workspace.
# stream_producer.properties.metadata["version"] = "Version 1"  # Add stream metadata to add context to time series data.

# Read the CSV data
df = pd.read_csv("ExampleData.csv")
date_col_name = 'datetime'  # Column name containing the timestamp information
# df = df.rename(columns={"username": "TAG__username" })  # Add TAG__ prefix to to use this column as tag (index).
print("File loaded.")

# Get original col names
original_cols = list(df.columns)
original_cols.remove(date_col_name)

# Now let's write this file to some stream in real time.
# We want to respect the original time deltas, so we'll need some calculations
# Get the timestamp data in timestamp format
df['Original_'+date_col_name] = pd.to_datetime(df[date_col_name])  # you may have to define format https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
df['Original_'+date_col_name] = [pd.Timestamp(ti, unit = 'ns').timestamp() for ti in df['Original_' + date_col_name]]
df = df.drop(date_col_name, axis = 1)

# Let's calculate the original time deltas and then the accumulated timedeltas
print("Calculating time deltas...")
df['delta_s_'+date_col_name] = df['Original_'+date_col_name].shift(-1) - df['Original_'+date_col_name]
df['acc_delta_s_'+date_col_name] = df['delta_s_'+date_col_name].expanding(1).sum()

# Let's generate the new timestamps
print("Generate new timestamps")
timestamp_now = pd.Timestamp.now().timestamp()
df['timestamp'] = (timestamp_now * 1e9) + (df['acc_delta_s_'+date_col_name] * 1e9)

def get_data():
    global df

    # Iterate over file
    while run:

        # this will end up loop when all data has been sent
        if df.empty:
            break

        # Get df_to_write
        filter_df_to_write = (df['timestamp'] <= pd.Timestamp.now().timestamp() * 1e9)

        # If there are rows to write to the stream at this time
        if filter_df_to_write.sum() > 0:

            # Get the rows to write and write them to the stream
            df_to_write = df.loc[filter_df_to_write, ['timestamp', 'Original_' + date_col_name] + original_cols]
            print("Writing {} rows of data".format(len(df_to_write)))

            stream_producer.timeseries.publish(df_to_write)
            print(df_to_write.to_string(index = False))

            # Update df
            df = df[filter_df_to_write == False]

        # If there are no rows to write now, wait a bit:
        else:
            # Calculate time to the next data point and wait that
            time_to_wait = df['delta_s_' + date_col_name].iloc[0]
            print("Waiting for ", time_to_wait, " seconds.")
            time.sleep(time_to_wait)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    # handle termination signals and close streams
    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()