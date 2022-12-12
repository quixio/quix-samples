from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader
from quixstreaming.app import App
from hugging_face_model import HuggingFaceModel
from transformers import pipeline
import os

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Download the Hugging Face model (list of available models here: https://huggingface.co/models)
model_name = os.environ["HuggingFaceModel"]
print("Downloading {0} model...".format(model_name))
model_pipeline = pipeline(model=model_name)

print("Opening input and output topics")
# Change consumer group to a different constant if you want to run model locally.
input_topic = client.open_input_topic(os.environ["input"], "default-consumer-group")
output_topic = client.open_output_topic(os.environ["output"])

# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):
    # Create a new stream to output data
    output_stream = output_topic.create_stream(input_stream.stream_id)
    output_stream.properties.parents.append(input_stream.stream_id)

    # handle the data in a function to simplify the example
    hugging_face_model = HuggingFaceModel(model_pipeline, input_stream, output_stream)

    # React to new data received from input topic.
    input_stream.events.on_read += hugging_face_model.on_event_data_handler
    input_stream.parameters.on_read += hugging_face_model.on_parameter_data_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(end_type: StreamEndType):
        output_stream.close()
        print("Stream closed:" + output_stream.stream_id)

    input_stream.on_stream_closed += on_stream_close


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()
