from quixstreaming import QuixStreamingClient
import pandas as pd
import time
import os

# Create a client. The client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# CREATE A NEW STREAM
# A stream is a collection of data that belong to a single session of a single source.
output_stream = output_topic.create_stream()

# If you want append data into the stream later, assign a stream id.
# stream = output_topic.create_stream("my-own-stream-id")

# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "ExampleData"

# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/example data"

# Add stream metadata to add context to time series data.
output_stream.properties.metadata["version"] = "Version 1"

# Read the CSV data
df = pd.read_csv("ExampleData.csv")
print("File loaded.")

# Add TAG__ prefix to column LapNumber to use this column as tag (index).
df = df.rename(columns={"username": "TAG__username" })

# Get original col names
original_cols = list(df.columns)
original_cols.remove(os.environ["DateColumnName"])

# Now let's write this file to some stream in real time.
# We want to respect the orginial time deltas, so we'll need some calculations
# Get the timestamp data in timestamp format
date_col_name = os.environ["DateColumnName"]
df['Original_'+date_col_name] = pd.to_datetime(df[date_col_name])  # you may have to define format https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
df = df.drop(date_col_name, axis=1)

# Let's calculate the original time deltas
print("Calculating time deltas...")
df['delta_'+date_col_name] = [delta for delta in df['Original_'+date_col_name].shift(-1)-df['Original_'+date_col_name]]
total = pd.Timedelta(0)
# Calculate accumulated timedeltas
for i, row in df.iterrows():
    total = total + row['delta_'+date_col_name]
    df.loc[i, 'acc_delta_'+date_col_name] = total

# Let's generate the new timestamps
print("Generate new timestamps")
df['timestamp'] = pd.Timestamp.now() + df['acc_delta_'+date_col_name]

# Iterate over file
while True:

    # this will end up loop when all data has been sent
    if df.empty:
        break

    # Get df_to_write
    filter_df_to_write = (df['timestamp'] <= pd.Timestamp.now())

    # If there are rows to write to the stream at this time
    if filter_df_to_write.sum() > 0:

        # Get the rows to write and write them to the stream
        df_to_write = df.loc[filter_df_to_write, ['timestamp', 'Original_'+date_col_name]+original_cols]
        print("Writing {} rows of data".format(len(df_to_write)))
        output_stream.parameters.write(df_to_write)

        # Update df
        df = df[filter_df_to_write == False]

    # If there are no rows to write now, wait a bit:
    else:
        # Calculate time to the next data point and wait that
        time_to_wait = df['delta_'+date_col_name].iloc[0].total_seconds()
        print("Waiting for ", time_to_wait, " seconds.")
        time.sleep(time_to_wait)


print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
output_stream.close()
