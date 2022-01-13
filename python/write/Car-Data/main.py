from quixstreaming import QuixStreamingClient
import pandas as pd
import os


# Create a client. The client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic("{}".format(os.environ["output"]))

# Create a new stream. A stream is a collection of data that belong to a single session of a single source.
# For example single car journey.
# If you don't specify a stream id, a random guid is used.
output_stream = output_topic.create_stream()

# If you want append data into the stream later, assign a stream id.
# stream = output_topic.create_stream("my-own-stream-id")

# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "cardata"

# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/static data"

# Add stream metadata to add context to time series data.
output_stream.properties.metadata["circuit"] = "Sakhir Short"
output_stream.properties.metadata["player"] = "Swal"
output_stream.properties.metadata["game"] = "Codemasters F1 2019"

# Read the CSV data
df = pd.read_csv("cardata.csv")

# Add TAG__ prefix to column LapNumber to use this column as tag (index).
df = df.rename(columns={"LapNumber": "TAG__LapNumber" })

# Write data frame to output topic.
print("Writing data")
output_stream.parameters.write(df)

print("Closing stream")

# Stream can be infinitely long or have start and end.
# If you send data into closed stream, it is automatically opened again.
output_stream.close()
