import quixstreams as qx
import time
import pandas as pd
import os


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

# If you want append data into the stream later, assign a stream id.
# stream = producer_topic.create_stream("my-own-stream-id")

# Give the stream human readable name. This name will appear in data catalogue.
stream_producer.properties.name = "cardata realtime"

# Save stream in specific folder in data catalogue to help organize your workspace.
stream_producer.properties.location = "/simulations"

# Add stream metadata to add context to time series data.
stream_producer.properties.metadata["circuit"] = "Sakhir Short"
stream_producer.properties.metadata["player"] = "Swal"
stream_producer.properties.metadata["game"] = "Codemasters F1 2019"

# Read the CSV data
df = pd.read_csv("cardata.csv")

# Add TAG__ prefix to column LapNumber to use this column as tag (index).
df = df.rename(columns={"LapNumber" : "TAG__LapNumber" })

# Add optional metadata to parameters.
stream_producer.timeseries.add_definition("Speed").set_range(0, 400).set_unit("KMH")
stream_producer.timeseries.add_definition("Gear").set_range(0, 9)
stream_producer.timeseries.add_definition("Steer").set_range(-1, 1)
stream_producer.timeseries.add_definition("EngineRPM").set_range(0, 14000)

# Every second we read one second worth of data from data frame and send it to the platform.
print("Writing data")
seconds_to_wait = float(os.environ["seconds_to_wait"])

for i in range(len(df)):
    start_loop = time.time()
    df_i = df.iloc[[i]]
    stream_producer.timeseries.publish(df_i)
    print("Sending " + str(i) + "/" + str(len(df)))
    end_loop = time.time()
    time.sleep(max(0.0, seconds_to_wait - (end_loop - start_loop)))

print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
stream_producer.close()
