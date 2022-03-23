from quixstreaming import QuixStreamingClient, StreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
import traceback
from datetime import datetime
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

    print("Opening RAW input topic")
    input_topic = kafka_client.open_raw_input_topic(os.environ["kafka_topic"])

    print("Opening output topic")
    output_topic = quix_client.open_output_topic(os.environ["output"])
    output_stream = output_topic.create_stream()
    output_stream.properties.location = "Confluent Kafka Data"
    output_stream.properties.name = "{} - {}".format("Confluent Kafka", datetime.utcnow().strftime("%d-%m-%Y %X"))

    is_connected = False

    quix_functions = QuixFunctions(output_stream)
    input_topic.on_message_read += quix_functions.raw_message_handler

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")

    # Handle graceful exit of the model.
    App.run()

    print("Exiting")

except Exception:
    print("ERROR: {}".format(traceback.format_exc()))
