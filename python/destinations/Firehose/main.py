import boto3
import json
import os
from botocore.config import Config
import quixstreams as qx


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"])

config = Config(
    region_name = os.environ["region"]
)

firehose = boto3.client(
    "firehose",
    aws_access_key_id = os.environ["aws_access_key_id"],
    aws_secret_access_key = os.environ["aws_secret_access_key"],
    config = config
)
stream_name = os.environ["stream_name"]
batch_msg_count = os.environ["batch_msg_count"]
print(f"Connecting to firehose stream {stream_name} with batch size {batch_msg_count}")


# read streams
def read_stream(stream_consumer: qx.StreamConsumer):
    print("New stream read:" + stream_consumer.stream_id)

    buffer_options = qx.TimeseriesBufferConfiguration()
    # DynamoDB BatchWriteItem has max 25 records as limit
    buffer_options.packet_size = batch_msg_count

    buffer = stream_consumer.timeseries.create_buffer(buffer_options)

    buffer.on_data_released = on_data_handler


def on_data_handler(stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
    items = []

    for ts in data.timestamps:
        item = {"timestamp": ts.timestamp_nanoseconds}

        for k, v in ts.parameters.items():
            if v.type == qx.ParameterValueType.String and v.string_value:
                item[k] = v.string_value
            if v.type == qx.ParameterValueType.Numeric and v.numeric_value is not None:
                item[k] = v.numeric_value

        for k, v in ts.tags.items():
            item["tag_" + k] = v

        record = (json.dumps(item) + "\n").encode('utf8')
        items.append({'Data': record})
    firehose.put_record_batch(DeliveryStreamName = stream_name, Records = items)


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
qx.App.run()
