import quixstreams as qx
from hugging_face_model import HuggingFaceModel
from transformers import pipeline
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Download the Hugging Face model (list of available models here: https://huggingface.co/models)
# suggested default is distilbert-base-uncased-finetuned-sst-2-english
model_name = os.environ["HuggingFaceModel"]
print("Downloading {0} model...".format(model_name))
model_pipeline = pipeline(model = model_name)

print("Opening input and output topics")
# Change consumer group to a different constant if you want to run model locally.
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group")
producer_topic = client.get_topic_producer(os.environ["output"])


# Callback called for each incoming stream
def read_stream(stream_consumer: qx.StreamConsumer):
    # Create a new stream to output data
    producer_stream = producer_topic.get_or_create_stream(stream_consumer.stream_id)
    producer_stream.properties.parents.append(stream_consumer.stream_id)

    # handle the data in a function to simplify the example
    hugging_face_model = HuggingFaceModel(model_pipeline, stream_consumer, producer_stream)

    # React to new data received from input topic.
    stream_consumer.events.on_data_received = hugging_face_model.on_event_data_handler
    stream_consumer.timeseries.on_data_received = hugging_face_model.on_parameter_data_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close():
        producer_stream.close()
        print("Stream closed:" + producer_stream.stream_id)

    stream_consumer.on_stream_closed = on_stream_close


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
