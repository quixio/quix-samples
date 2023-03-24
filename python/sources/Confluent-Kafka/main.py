import quixstreams as qx
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

    quix_client = qx.QuixStreamingClient()

    print("Opening RAW input topic")
    consumer_topic = kafka_client.open_raw_consumer_topic(os.environ["kafka_topic"])

    print("Opening output topic")
    producer_topic = quix_client.get_topic_producer(os.environ["output"])
    stream_producer = producer_topic.create_stream()
    stream_producer.properties.location = "Confluent Kafka Data"
    stream_producer.properties.name = "{} - {}".format("Confluent Kafka", datetime.utcnow().strftime("%d-%m-%Y %X"))

    is_connected = False

    quix_functions = QuixFunctions(stream_producer)
    consumer_topic.on_message_read += quix_functions.raw_message_handler

    # let the platform know were connected. It will navigate to the home page.
    print("CONNECTED!")

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")

    # Handle graceful exit of the model.
    qx.App.run()

    print("Exiting")

except Exception:
    print("ERROR: {}".format(traceback.format_exc()))
