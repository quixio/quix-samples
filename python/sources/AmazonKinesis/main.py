from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
import boto3
from datetime import datetime
import traceback
import time
import threading
import os

# should the main loop keep running?
run = True

subscriber = None
subscription = None
quix_stream = None
amazon_client = None
output_topic = None


def connect_to_amazon():
    global amazon_client

    if quix_stream is None:
        print("Not connected to Quix")
        return False

    amazon_client = boto3.client(
        'kinesis',
        aws_access_key_id=os.environ["aws_access_key_id"],
        aws_secret_access_key=os.environ["aws_secret_access_key"],
        region_name=os.environ["aws_region_name"]
    )


def get_kinesis_data():

    if quix_stream is None:
        print("Not connected to Quix")
        return False

    quix_functions = QuixFunctions(output_topic)

    si = amazon_client.get_shard_iterator(
        StreamName=os.environ["aws_stream_name"],
        ShardId='shardId-000000000000',
        ShardIteratorType='LATEST'
    )

    shard_iterator = si["ShardIterator"]
    while run:
        record_data = amazon_client.get_records(ShardIterator=shard_iterator)
        shard_iterator = record_data["NextShardIterator"]

        print(record_data)
        if len(record_data["Records"]) > 0:

            for r in record_data["Records"]:
                quix_functions.write_data(r["Data"])

        behind = record_data["MillisBehindLatest"]
        if behind < 1000:
            time.sleep(1)
        else:
            time.sleep(0.1)


def connect_to_quix():
    global quix_stream
    global output_topic

    quix_client = QuixStreamingClient()

    print("Opening output topic")
    output_topic = quix_client.open_output_topic(os.environ["output"])
    quix_stream = output_topic.create_stream()
    quix_stream.properties.name = "{} - {}".format("Amazon Kinesis", datetime.utcnow().strftime("%d-%m-%Y %X"))
    quix_stream.properties.location = "/amazon_kinesis_data"


def before_shutdown():
    global run
    run = False


try:
    connect_to_quix()
    connect_to_amazon()

    thread = threading.Thread(target=get_kinesis_data)
    thread.start()

    print("Waiting for Kinesis data")

    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print('Exiting')

except:
    print("ERROR: {}".format(traceback.format_exc()))

