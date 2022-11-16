import boto3
import json
import os
from botocore.config import Config
from quixstreaming import QuixStreamingClient, StreamReader, ParameterData, ParameterValueType
from quixstreaming.app import App
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])

config = Config(
    region_name=os.environ["region"]
)

firehose = boto3.client(
    "firehose",
    aws_access_key_id=os.environ["aws_access_key_id"],
    aws_secret_access_key=os.environ["aws_secret_access_key"],
    config=config
)
stream_name = os.environ["stream_name"]
batch_msg_count = os.environ["batch_msg_count"]
print(f"Connecting to firehose stream {stream_name} with batch size {batch_msg_count}")


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    buffer_options = ParametersBufferConfiguration()
    # DynamoDB BatchWriteItem has max 25 records as limit
    buffer_options.packet_size = batch_msg_count

    buffer = input_stream.parameters.create_buffer(buffer_options)

    buffer.on_read += on_parameter_data_handler


def on_parameter_data_handler(data: ParameterData):
    items = []

    for ts in data.timestamps:
        item = {"timestamp": ts.timestamp_nanoseconds}

        for k, v in ts.parameters.items():
            if v.type == ParameterValueType.String and v.string_value:
                item[k] = v.string_value
            if v.type == ParameterValueType.Numeric and v.numeric_value is not None:
                item[k] = v.numeric_value

        for k, v in ts.tags.items():
            item["tag_" + k] = v

        record = (json.dumps(item) + "\n").encode('utf8')
        items.append({'Data': record})
    firehose.put_record_batch(DeliveryStreamName=stream_name, Records=items)


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()
