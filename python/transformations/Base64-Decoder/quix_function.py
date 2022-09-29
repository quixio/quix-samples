from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd
import base64

class QuixFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        # Here transform your data.

        self.output_stream.events.write(data)

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df: pd.DataFrame):
        
        df['image'] = df["image"].apply(lambda x: base64.b64decode(x))
        self.output_stream.parameters.write(df)
