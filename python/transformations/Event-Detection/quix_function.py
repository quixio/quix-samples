from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd


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
    def on_parameter_data_handler(self, data: ParameterData):
        
        df = data.to_panda_frame()  # Input data frame
        output_df = pd.DataFrame()
        output_df["time"] = df["time"]

        if "TAG__LapNumber" in df.columns:
            output_df["TAG__LapNumber"] = df["TAG__LapNumber"]
            
        print(df)

        # If braking force applied is more than 50%, we send True.  
        if "Brake" in df.columns:
            output_df["HardBraking"] = df.apply(lambda row: "True" if row.Brake > 0.5 else "False", axis=1)  

        self.output_stream.parameters.buffer.write(output_df)  # Send filtered data to output topic

