from quixstreaming import QuixStreamingClient
import time
import pandas as pd
import os


# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# Create a new output_stream. A stream is a collection of data that belong to a single session of a single source.
# For example single car journey.
# If you don't specify a stream id, a random guid is used.
output_stream = output_topic.create_stream()

# If you want append data into the stream later, assign a stream id.
# stream = output_topic.create_stream("my-own-stream-id")

# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "cardata realtime"

# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/simulations"

# Add stream metadata to add context to time series data.
output_stream.properties.metadata["circuit"] = "Sakhir Short"
output_stream.properties.metadata["player"] = "Swal"
output_stream.properties.metadata["game"] = "Codemasters F1 2019"

# Read the CSV data
df = pd.read_csv("cardata.csv")

# Add TAG__ prefix to column LapNumber to use this column as tag (index).
df = df.rename(columns={"LapNumber" : "TAG__LapNumber" })

# Add optional metadata to parameters.
output_stream.parameters.add_definition("Speed").set_range(0, 400).set_unit("KMH")
output_stream.parameters.add_definition("Gear").set_range(0, 9)
output_stream.parameters.add_definition("Steer").set_range(-1, 1)
output_stream.parameters.add_definition("EngineRPM").set_range(0, 14000)

# Every second we read one second worth of data from data frame and send it to the platform.
print("Writing data")
seconds_to_wait = float(os.environ["seconds_to_wait"])

for i in range(len(df)):
    start_loop = time.time()
    df_i = df.iloc[[i]]
    output_stream.parameters.write(df_i)
    print("Sending " + str(i) + "/" + str(len(df)))
    end_loop = time.time()
    time.sleep(max(0.0, seconds_to_wait - (end_loop - start_loop)))

print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
output_stream.close()
