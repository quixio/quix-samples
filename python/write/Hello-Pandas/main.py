from quixstreaming import QuixStreamingClient
from datetime import datetime
import pandas as pd
import os


# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic and create the stream
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])
output_stream = output_topic.create_stream()

# We can optionally name the stream
output_stream.properties.name = "Hello Panda stream"

# We can optionally set the epoch
output_stream.parameters.epoch = datetime.utcnow()
df = pd.DataFrame({'time': [0, 1000000000, 2000000000, 3000000000, 4000000000, 5000000000, 6000000000, 7000000000],
                   'ParameterA': [121, 55.68, 60, 78.9234, 85, 65, 50, 40]})

print("Writing data")
output_stream.parameters.write(df)

print("Closing stream")
output_stream.close()
print("Done!")
