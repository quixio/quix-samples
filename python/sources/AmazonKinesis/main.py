import quixstreams as qx
from kinesis_functions import KinesisFunctions
from datetime import datetime
import traceback
import threading
import os

quix_stream: qx.streamproducer = None


def connect_to_quix() -> qx.streamproducer:
    quix_client = qx.QuixStreamingClient()

    print("Opening output topic")
    output_topic = quix_client.get_topic_producer(os.environ["output"])

    stream = output_topic.create_stream()
    stream.properties.name = "{} - {}".format("AWS Kinesis", datetime.utcnow().strftime("%d-%m-%Y %X"))
    stream.properties.location = "/aws_kinesis_data"

    return stream


# handle kinesis data
def data_handler(data):
    print("Publishing RAW event data to Quix")

    try:
        event_data = qx.EventData(event_id="raw_data", time=datetime.utcnow(), value=str(data))
        quix_stream.events.publish(event_data)
    except BaseException:
        print(traceback.format_exc())


if __name__ == '__main__':

    try:
        def before_shutdown():
            kinesis.stop_running()


        quix_stream = connect_to_quix()

        kinesis = KinesisFunctions(quix_stream, data_handler=data_handler)

        kinesis.connect()

        thread = threading.Thread(target=kinesis.get_data)
        thread.start()

        print("Waiting for Kinesis data")

        qx.App.run(before_shutdown=before_shutdown)

        # wait for worker thread to end
        thread.join()

        print('Exiting')

    except BaseException:
        print("ERROR: {}".format(traceback.format_exc()))
