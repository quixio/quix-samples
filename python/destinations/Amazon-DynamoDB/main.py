import boto3
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError
from botocore.config import Config
from quixstreaming import QuixStreamingClient, StreamReader, ParameterData, ParameterValueType
from quixstreaming.app import App
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])

config = Config(
    region_name=os.environ["region"],
    retries={
        'max_attempts': 5,
        'mode': 'adaptive'
    }
)

dynamodb = boto3.client(
    "dynamodb",
    aws_access_key_id=os.environ["aws_access_key_id"],
    aws_secret_access_key=os.environ["aws_secret_access_key"],
    config=config
)

if "table_name" not in os.environ or os.environ["table_name"] == "":
    print("Environment variable table_name not set. Creating new DynamoDB table quix-" + os.environ["input"])
    table_name = "quix-" + os.environ["input"]
    try:
        dynamodb.create_table(TableName=table_name, AttributeDefinitions=[{"AttributeName": "date", "AttributeType": "S"},
                                                                          {"AttributeName": "time", "AttributeType": "S"}],
                              KeySchema=[{"AttributeName": "date", "KeyType": "HASH"},
                                         {"AttributeName": "time", "KeyType": "RANGE"}], BillingMode="PAY_PER_REQUEST",
                              SSESpecification={"Enabled": True, "SSEType": "KMS"})
        print("Create table request sent for DynamoDB table: quix-" + os.environ["input"])
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Skipping table ceration as table with name "+table_name+" already exists.")
        else:
            print(e)
else:
    table_name = os.environ["table_name"]


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    buffer_options = ParametersBufferConfiguration()
    buffer_options.packet_size = 25

    buffer = input_stream.parameters.create_buffer(buffer_options)

    buffer.on_read += on_parameter_data_handler


def on_parameter_data_handler(data: ParameterData):
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
            if v.type == ParameterValueType.String and v.string_value:
                item[k] = {"S": v.string_value}
            if v.type == ParameterValueType.Numeric and v.numeric_value is not None:
                item[k] = {"N": str(ts.parameters[k].numeric_value)}
        items.append({"PutRequest": {"Item": item}})
    batch_write({table_name: items})


def batch_write(request, retry_count=1):
    try:
        response = dynamodb.batch_write_item(RequestItems=request)
        if "UnprocessedItems" in response and len(response["UnprocessedItems"]) > 0:
            if retry_count < os.environ["max_retry"]:
                print("Try: [" + retry_count + "] Retrying " + len(response["UnprocessedItems"]) + " unprocessed items")
                time.sleep(retry_count)
                batch_write(response["UnprocessedItems"], retry_count + 1)
            else:
                print("Failed writing to DynamoDB table. Max retries reached.")
    except Exception as e:
        print(e)


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()
