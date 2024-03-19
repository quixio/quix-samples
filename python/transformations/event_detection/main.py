import os
from quixstreams import Application, State
from datetime import datetime
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix("hard-braking-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer='json')
output_topic = app.topic(os.environ["output"], value_serializer='json')

sdf = app.dataframe(input_topic)

# Filter items out without brake value.
sdf = sdf[sdf["Brake"].notnull()] 

# Calculate hopping window of 1s with 200ms steps.
sdf = sdf.apply(lambda row: row["Brake"]) \
        .hopping_window(1000, 200).mean().final() 

# Filter only windows where average brake force exceeded 50%.
sdf = sdf[sdf["value"] > 0.5]

# Create nice JSON alert message.
sdf = sdf.apply(lambda row: {
    "Timestamp": str(datetime.fromtimestamp(row["start"]/1000)),
    "Alert": {
        "Title": "Hard braking detected.",
        "Message": "For last 1 second, average braking power was " + str(row["value"])
    }
})

# Print JSON messages in console.
sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

# Send the message to the output topic
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)