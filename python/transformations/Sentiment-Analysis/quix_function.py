from quixstreaming import StreamReader, StreamWriter, EventData, LocalFileStorage
from transformers import Pipeline

class QuixFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter, classifier: Pipeline):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.classifier = classifier
        
        self.storage = LocalFileStorage()
        if self.storage.containsKey(input_stream.stream_id + "-sum"):
            self.sum = int(self.storage.get(self.input_stream.stream_id + "-sum"))
            self.count = int(self.storage.get(self.input_stream.stream_id + "-count"))
            print("State loaded from storage.")
        else:
            self.sum = 0
            self.count = 0
            print("No state found in storage.")

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        sent = self.classifier(data.value)
        label = sent[0]['label']
        score = sent[0]['score']

        # Invert the negative score so that graph looks better
        if (label == 'NEGATIVE'):
            score = score - (score * 2)

        print(score)

        self.sum = self.sum + score
        self.count = self.count + 1

        self.output_stream.parameters.buffer.add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
            .add_tags(data.tags) \
            .add_value("chat-message", data.value.upper()) \
            .add_value("sentiment", score) \
            .add_value("average_sentiment", self.sum / self.count) \
            .write()

    def on_committed(self):
        self.storage.set(self.input_stream.stream_id + "-sum", self.sum)
        self.storage.set(self.input_stream.stream_id + "-count", self.count)
        print("State persisted in storage.")
