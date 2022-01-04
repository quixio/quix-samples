from quixstreaming import StreamReader,StreamWriter, EventData, ParameterData

class QuixFunction:
    def __init__(self, stream_writer: StreamWriter, stream_reader: StreamReader):
        self.stream_writer = stream_writer
        self.stream_reader = stream_reader


    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        # Here transform your data.

        self.stream_writer.events.write(data)

     # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        
        df = data.to_panda_frame()  # Input data frame
        output_df = pd.DataFrame()
        output_df["time"] = df["time"]

        output_df["TAG__LapNumber"] = df["TAG__LapNumber"]
        print(df)

        # If braking force applied is more than 50%, we send True.  
        output_df["HardBraking"] = df.apply(lambda row: "True" if row.Brake > 0.5 else "False", axis=1)  

        stream_writer.parameters.buffer.write(output_df)  # Send filtered data to output topic

