from quixstreaming import StreamReader, OutputTopic, EventData
import pandas as pd
import base64

class QuixFunction:
    def __init__(self, input_stream: StreamReader, output_topic: OutputTopic):
        self.input_stream = input_stream
        self.output_topic = output_topic

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        # Here transform your data.

        self.output_stream.events.write(data)

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df: pd.DataFrame):

        df["TAG__parent_streamId"] = self.input_stream.stream_id
        df['image'] = df["image"].apply(lambda x: str(base64.b64encode(x).decode('utf-8')))

        self.output_topic.get_or_create_stream("image-feed") \
            .parameters.buffer.write(df)
