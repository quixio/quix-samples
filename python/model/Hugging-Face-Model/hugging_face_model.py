from quixstreaming import StreamReader, StreamWriter, EventData
from transformers import pipeline
import os


class HuggingFaceModel:

    # Initiate
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.model = pipeline(model=os.environ["HuggingFaceModel"])

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

        # Call model with message payload.
        sent = self.model(data.value)

        label = sent[0]['label']
        score = sent[0]['score']

        # Invert the negative score so that graph looks better
        if label == 'NEGATIVE':
            score = score - (score * 2)

        # Write df to output stream
        self.output_stream.parameters.buffer \
            .add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
            .add_tags(data.tags) \
            .add_value("chat-message", data.value) \
            .add_value("sentiment", score) \
            .write()
