import os
from streamingdataframes import Application, MessageContext, State
from streamingdataframes.models.rows import Row
from streamingdataframes.models.serializers import (
    QuixTimeseriesSerializer,
    QuixDeserializer,
    JSONDeserializer
)

app = Application.Quix("big-query-sink-v5", auto_offset_reset="latest", )
input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())
output_topic = app.topic(os.environ["output"], value_serializer=QuixTimeseriesSerializer())


sdf = app.dataframe(input_topic)

sdf.apply(lambda row,ctx: print(row))  # easy way to print out

sdf.to_topic(output_topic)

print("Listening to streams. Press CTRL-C to exit.")
app.run(sdf)