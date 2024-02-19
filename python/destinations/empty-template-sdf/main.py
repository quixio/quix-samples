import os
from quixstreams import Application, State
from quixstreams.models.serializers.quix import QuixDeserializer, QuixTimeseriesSerializer


app = Application.Quix("destination-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())

sdf = app.dataframe(input_topic)

# Sink to your destination here!

sdf = sdf.update(lambda row: print(row))

if __name__ == "__main__":
    app.run(sdf)