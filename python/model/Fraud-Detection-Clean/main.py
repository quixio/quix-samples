from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.models import StreamEndType
from quixstreaming.app import App
from quix_function import QuixFunction
import os

output_topic = None


def read_stream(new_stream: StreamReader):

    # create the output stream with an ID based on the input stream ID
    output_stream = output_topic.create_stream(new_stream.stream_id + "-cleandata-out-stream")

    output_stream.properties.name = "clean_data"
    output_stream.properties.location = "/dataset/clean_data"

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
    output_topic = streamingClient.open_output_topic(os.environ["output"])
    input_topic = streamingClient.open_input_topic(os.environ["input"])

    input_topic.on_stream_received += read_stream
    input_topic.start_reading()  # initiate read

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")
    App.run()
    print("Exiting")


if __name__ == "__main__":
    main()
    pass
