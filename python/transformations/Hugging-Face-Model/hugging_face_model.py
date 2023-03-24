import quixstreams as qx
from transformers import Pipeline
import os


class HuggingFaceModel:

    # Initiate
    def __init__(self, model_pipeline: Pipeline, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer
        self.model = model_pipeline
        self.text_column_name = os.environ["TextColumnName"]

    # triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data)

        # Call model with message payload.
        prediction = self.model(data.value)[0]

        label = prediction['label']
        score = prediction['score']

        # Publish df to output stream
        self.stream_producer.timeseries.buffer \
            .add_timestamp_nanoseconds(data.timestamp_nanoseconds) \
            .add_value("label", label) \
            .add_value("sentiment", score) \
            .add_tags(data.tags) \
            .publish()

    # triggered for each new timeseries data.
    def on_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):

        for row in data.timestamps:
            print(row)

            # Call model with message payload.
            prediction = self.model(row.parameters[self.text_column_name].string_value)[0]

            label = prediction['label']
            score = prediction['score']
            print(prediction)

            self.workaround_tags_bug(row)

            # Write df to output stream
            self.stream_producer.timeseries.buffer \
                .add_timestamp_nanoseconds(row.timestamp_nanoseconds) \
                .add_value("label", label) \
                .add_value("sentiment", score) \
                .add_tags(row.tags) \
                .publish()

    def workaround_tags_bug(self, row: qx.TimeseriesDataTimestamp):
        # remove when https://github.com/quixio/quix-streams/issues/62 fixed
        # ensure there are no empty tags
        tags_to_pop = []
        for t in row.tags:
            if row.tags[t] == "":
                tags_to_pop.append(t)

        for t in tags_to_pop:
            row.tags.pop(t)
