from quixstreaming import QuixStreamingClient, StreamingClient, StreamReader
from quixstreaming.app import App
from quix_function import QuixFunctions
import traceback
import os

try:
    kafka_properties = {
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": os.environ["kafka_key"],
        "sasl.password": os.environ["kafka_secret"]
    }

    kafka_client = StreamingClient(os.environ["kafka_broker_address"],
                                   None,
                                   kafka_properties)

    quix_client = QuixStreamingClient()

    print("Opening RAW output topic")
    output_topic = kafka_client.open_raw_output_topic(os.environ["kafka_topic"])

    input_topic = quix_client.open_input_topic(os.environ["input"])

    is_connected = False

    quix_functions = QuixFunctions(output_topic)

    # Callback called for each incoming stream
    def read_stream(input_stream: StreamReader):

        print("New input stream detected")

        # handle the data in a function to simplify the example
        mqtt_function = QuixFunctions(output_topic)

        # hookup the package received event handler
        input_stream.on_package_received += mqtt_function.package_received_handler

    # hookup the callback to handle new streams
    input_topic.on_stream_received += read_stream

    print("CONNECTED!")

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")

    # Handle graceful exit of the model.
    App.run()

    print("Exiting")

except Exception:
    print("ERROR: {}".format(traceback.format_exc()))
