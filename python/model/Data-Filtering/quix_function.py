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
        print(data)

        # Here transform your data.

        self.stream_writer.parameters.write(data)

