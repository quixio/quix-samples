from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.models import StreamEndType
from quixstreaming.app import App
from quix_function import QuixFunction
import os

PREDICT_STREAM_NAME = "predict_data"
PREDICT_STREAM_PATH = "/dataset/predict_data"
PREDICT_STREAM_ID = "-predict-out-stream"

output_topic = None


def read_stream(new_stream: StreamReader):
    output_stream = output_topic.create_stream(new_stream.stream_id + PREDICT_STREAM_ID)

    output_stream.properties.name = PREDICT_STREAM_NAME
    output_stream.properties.location = PREDICT_STREAM_PATH

    buffer_options = ParametersBufferConfiguration()
    buffer_options.buffer_timeout = 1000

    buffer = new_stream.parameters.create_buffer(buffer_options)

    quix_function = QuixFunction(output_stream)

    # React to new data received from input topic.
    buffer.on_read_pandas += quix_function.on_pandas_frame_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(end_type: StreamEndType):
        output_stream.close(end_type)
        print("Stream closed:" + output_stream.stream_id)

    new_stream.on_stream_closed += on_stream_close


def main():
    global output_topic

    streamingClient = QuixStreamingClient()

    input_topic = streamingClient.open_input_topic(os.environ["input"])
    output_topic = streamingClient.open_output_topic(os.environ["output"])

    # Hook up events before initiating read to avoid losing out on any data
    input_topic.on_stream_received += read_stream

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")
    App.run()
    print("Exiting")


if __name__ == "__main__":
    main()
    pass
