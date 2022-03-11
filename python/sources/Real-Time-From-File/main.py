from quixstreaming import QuixStreamingClient
import pandas as pd
import time
import os

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# CREATE A NEW STREAM
# A stream is a collection of data that belong to a single session of a single source.
output_stream = output_topic.create_stream()
# EDIT STREAM
# stream = output_topic.create_stream("my-own-stream-id")  # To append data into the stream later, assign a stream id.
output_stream.properties.name = "ExampleData"  # Give the stream a human readable name (for the data catalogue).
output_stream.properties.location = "/example data"  # Save stream in specific folder to organize your workspace.
# output_stream.properties.metadata["version"] = "Version 1"  # Add stream metadata to add context to time series data.

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
df['Original_'+date_col_name] = [pd.Timestamp(ti, unit='ns').timestamp() for ti in df['Original_'+date_col_name]]
df = df.drop(date_col_name, axis=1)

# Let's calculate the original time deltas and then the accumulated timedeltas
print("Calculating time deltas...")
df['delta_s_'+date_col_name] = df['Original_'+date_col_name].shift(-1)-df['Original_'+date_col_name]
df['acc_delta_s_'+date_col_name] = df['delta_s_'+date_col_name].expanding(1).sum()

# Let's generate the new timestamps
print("Generate new timestamps")
timestamp_now = pd.Timestamp(pd.Timestamp.now(), unit='ns').timestamp()
df['timestamp'] = timestamp_now + df['acc_delta_s_'+date_col_name]

# Iterate over file
while True:

    # this will end up loop when all data has been sent
    if df.empty:
        break

    # Get df_to_write
    filter_df_to_write = (df['timestamp'] <= pd.Timestamp(pd.Timestamp.now(), unit='ns').timestamp())

    # If there are rows to write to the stream at this time
    if filter_df_to_write.sum() > 0:

        # Get the rows to write and write them to the stream
        df_to_write = df.loc[filter_df_to_write, ['timestamp', 'Original_'+date_col_name]+original_cols]
        print("Writing {} rows of data".format(len(df_to_write)))
        output_stream.parameters.write(df_to_write)
        print(df_to_write.to_string(index=False))

        # Update df
        df = df[filter_df_to_write == False]

    # If there are no rows to write now, wait a bit:
    else:
        # Calculate time to the next data point and wait that
        time_to_wait = df['delta_s_'+date_col_name].iloc[0]
        print("Waiting for ", time_to_wait, " seconds.")
        time.sleep(time_to_wait)


print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
output_stream.close()