import quixstreams as qx
import boto3
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError
from botocore.config import Config

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"])

config = Config(
    region_name = os.environ["region"],
    retries = {
        'max_attempts': 5,
        'mode': 'adaptive'
    }
)

dynamodb = boto3.client(
    "dynamodb",
    aws_access_key_id = os.environ["aws_access_key_id"],
    aws_secret_access_key = os.environ["aws_secret_access_key"],
    config = config
)

if "table_name" not in os.environ or os.environ["table_name"] == "":
    print("Environment variable table_name not set. Creating new DynamoDB table quix-" + os.environ["input"])
    table_name = "quix-" + os.environ["input"]
    try:
        partition_key = os.environ["param_partition_key"].split("|")[0]
        if "param_sort_key" not in os.environ or os.environ["param_sort_key"] == "":
            dynamodb.create_table(TableName = table_name,
                                  AttributeDefinitions=[{"AttributeName": partition_key, "AttributeType": "S"}],
                                  KeySchema=[{"AttributeName": partition_key, "KeyType": "HASH"}],
                                  BillingMode = "PAY_PER_REQUEST",
                                  SSESpecification={"Enabled": True, "SSEType": "KMS"})
        else:
            sort_key = os.environ["param_sort_key"].split("|")[0]
            dynamodb.create_table(TableName = table_name,
                                  AttributeDefinitions=[{"AttributeName": partition_key, "AttributeType": "S"},
                                                        {"AttributeName": sort_key, "AttributeType": "S"}],
                                  KeySchema=[{"AttributeName": partition_key, "KeyType": "HASH"},
                                             {"AttributeName": sort_key, "KeyType": "RANGE"}],
                                  BillingMode = "PAY_PER_REQUEST",
                                  SSESpecification={"Enabled": True, "SSEType": "KMS"})
        print("Create table request sent for DynamoDB table: quix-" + os.environ["input"])
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Skipping table creation as table with name " + table_name + " already exists.")
        else:
            print(e)
else:
    table_name = os.environ["table_name"]


# read streams
def read_stream(stream_consumer: qx.StreamConsumer):
    print("New stream read:" + stream_consumer.stream_id)

    buffer_options = qx.TimeseriesBufferConfiguration()
    # DynamoDB BatchWriteItem has max 25 records as limit
    buffer_options.packet_size = 25

    buffer = stream_consumer.timeseries.create_buffer(buffer_options)

    buffer.on_data_released = on_data_handler


def on_data_handler(stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
    items = []

    for ts in data.timestamps:
        item = {}
        timestamp = datetime.fromtimestamp(ts.timestamp_nanoseconds / 1000000000)

        if "|" in os.environ["param_partition_key"]:
            key = os.environ["param_partition_key"].split("|")[0]
            pattern = os.environ["param_partition_key"].split("|")[1]
            item[key] = {"S": timestamp.strftime(pattern)}
        if "|" in os.environ["param_sort_key"]:
            key = os.environ["param_sort_key"].split("|")[0]
            pattern = os.environ["param_sort_key"].split("|")[1]
            item[key] = {"S": timestamp.strftime(pattern)}

        for k, v in ts.parameters.items():
            if v.type == qx.ParameterValueType.String and v.string_value:
                item[k] = {"S": v.string_value}
            if v.type == qx.ParameterValueType.Numeric and v.numeric_value is not None:
                item[k] = {"N": str(ts.parameters[k].numeric_value)}

        for k, v in ts.tags.items():
            item["tag__" + k] = {"S": v}
        items.append({"PutRequest": {"Item": item}})
    batch_write({table_name: items})


def batch_write(request, retry_count = 1):
    try:
        response = dynamodb.batch_write_item(RequestItems = request)
        if "UnprocessedItems" in response and len(response["UnprocessedItems"]) > 0:
            if retry_count < os.environ["max_retry"]:
                print("Try: [" + retry_count + "] Retrying " + len(response["UnprocessedItems"]) + " unprocessed items")
                time.sleep(retry_count)
                batch_write(response["UnprocessedItems"], retry_count + 1)
            else:
                print("Failed writing to DynamoDB table. Max retries reached.")
    except Exception as e:
        print(f'Request -> {request}')
        print(e)


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
qx.App.run()
