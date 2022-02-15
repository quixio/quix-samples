from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
from transformers import pipeline
import os


class HuggingFaceModel:

    # Initiate
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.model = pipeline(model=os.environ["HuggingFaceModel"])
        self.text_column_name = os.environ["TextColumnName"]

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

        # Call model with message payload.
        sent = self.model(data.value)

        label = sent[0]['label']
        score = sent[0]['score']

        # Write df to output stream
        self.output_stream.parameters.buffer \
            .add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
            .add_tags(data.tags) \
            .add_value("label", label) \
            .add_value("sentiment", score) \
            .write()

    # Callback triggered for each new table data.
    def on_parameter_data_handler(self, data: ParameterData):

        for row in data.timestamps:
            print(row)

            # Call model with message payload.
            sent = self.model(data.parameters[self.text_column_name])

            label = sent[0]['label']
            score = sent[0]['score']

            print(sent)

            # Write df to output stream
            self.output_stream.parameters.buffer \
                .add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
                .add_tags(data.tags) \
                .add_value("label", label) \
                .add_value("sentiment", score) \
                .write()
