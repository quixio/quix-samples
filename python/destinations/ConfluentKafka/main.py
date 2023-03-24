import quixstreams as qx
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

    quix_client = qx.QuixStreamingClient()

    print("Opening RAW output topic")
    producer_topic = kafka_client.open_raw_producer_topic(os.environ["kafka_topic"])

    consumer_topic = quix_client.get_topic_consumer(os.environ["input"])

    is_connected = False

    quix_functions = QuixFunctions(producer_topic)

    # Callback called for each incoming stream
    def read_stream(stream_consumer: qx.StreamConsumer):

        print("New input stream detected")

        # handle the data in a function to simplify the example
        quix_function = QuixFunctions(producer_topic)

        # hookup the package received event handler
        stream_consumer.on_package_received += quix_function.package_received_handler

    # hookup the callback to handle new streams
    consumer_topic.on_stream_received = read_stream

    print("CONNECTED!")

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")

    # Handle graceful exit of the model.
    qx.App.run()

    print("Exiting")

except Exception:
    print("ERROR: {}".format(traceback.format_exc()))
