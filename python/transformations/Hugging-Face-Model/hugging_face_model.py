from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
from transformers import Pipeline
import os


class HuggingFaceModel:

    # Initiate
    def __init__(self, model_pipeline: Pipeline, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.model = model_pipeline
        self.text_column_name = os.environ["TextColumnName"]

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

        # Call model with message payload.
        prediction = self.model(data.value)[0]

        label = prediction['label']
        score = prediction['score']

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
            prediction = self.model(row.parameters[self.text_column_name].string_value)[0]

            label = prediction['label']
            score = prediction['score']
            print(prediction)

            # Write df to output stream
            self.output_stream.parameters.buffer \
                .add_timestamp_nanoseconds(row.timestamp_nanoseconds) \
                .add_tags(row.tags) \
                .add_value("label", label) \
                .add_value("sentiment", score) \
                .write()
