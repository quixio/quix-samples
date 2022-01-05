from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.app import App
from quix_function import QuixFunction

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')
# temporary (needed for dev)
client.api_url = "https://portal-api.dev.quix.ai"

<<<<<<< HEAD
input_topic = client.open_input_topic('{placeholder:workspaceId}-{placeholder:input}')
=======
input_topic = client.open_input_topic(os.environ[])
>>>>>>> quix-function


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    buffer_options = ParametersBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100

    buffer = input_stream.parameters.create_buffer(buffer_options)

    quix_function = QuixFunction()

    buffer.on_read += quix_function.on_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()
