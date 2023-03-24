import quixstreams as qx
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"])

config = Config(
    region_name = os.environ["region"]
)

timestream = boto3.client(
    "timestream-write",
    aws_access_key_id = os.environ["aws_access_key_id"],
    aws_secret_access_key = os.environ["aws_secret_access_key"],
    config = config
)

database_name = os.environ["database_name"]
batch_size = int(os.environ["batch_size"])

if batch_size < 1 or batch_size > 100:
    print("Invalid batch_size set. Must be between 1 to 100")
    exit(0)


try:
    print(f"Trying to create database with name = {database_name}")
    timestream.create_database(DatabaseName = database_name)
except ClientError as e:
    if e.response['Error']['Code'] == 'ConflictException':
        print(f"Database {database_name} already present.")
    else:
        print(e)

if "table_name" not in os.environ or os.environ["table_name"] == "":
    table_name = os.environ["input"]
else:
    table_name = os.environ["table_name"]

try:
    print(f"Trying to create table with name = {table_name} in database {database_name}")
    timestream.create_table(DatabaseName = database_name, TableName = table_name,
                            MagneticStoreWriteProperties={
                                "EnableMagneticStoreWrites": True
                            },
                            RetentionProperties={
                                "MemoryStoreRetentionPeriodInHours": int(os.environ["mem_store_retention_hours"]),
                                "MagneticStoreRetentionPeriodInDays": int(os.environ["disk_store_retention_days"])})
except ClientError as e:
    if e.response['Error']['Code'] == 'ConflictException':
        print(f"Table {table_name} already present.")
    else:
        print(e)


# read streams
def read_stream(stream_consumer: qx.StreamConsumer):
    def on_data_handler(stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
        records = []

        for ts in data.timestamps:
            record = {"Time": str(ts.timestamp_nanoseconds), "TimeUnit": "NANOSECONDS"}
            dimensions = [{"Name": "stream_id", "Value": stream_consumer.stream_id}]

            for k, v in ts.tags.items():
                if k != "strem_id":
                    dimensions.append({"Name": k, "Value": v})

            if len(dimensions) > 0:
                record["Dimensions"] = dimensions

            for k, v in ts.parameters.items():
                if v.type == qx.ParameterValueType.String and v.string_value:
                    record["MeasureName"] = k
                    record["MeasureValue"] = v.string_value
                    record["MeasureValueType"] = "VARCHAR"
                if v.type == qx.ParameterValueType.Numeric and v.numeric_value is not None:
                    record["MeasureName"] = k
                    record["MeasureValue"] = str(v.numeric_value)
            records.append(record)

        try:
            result = timestream.write_records(DatabaseName = database_name, TableName = table_name, Records = records)
            print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
        except timestream.exceptions.RejectedRecordsException as err:
            print_rejected_records_exceptions(err)
        except Exception as err:
            print("Error:", err)
            
    print("New stream read:" + stream_consumer.stream_id)

    buffer_options = qx.TimeseriesBufferConfiguration()
    buffer_options.packet_size = batch_size

    buffer = stream_consumer.timeseries.create_buffer(buffer_options)

    buffer.on_data_released =  on_data_handler


def print_rejected_records_exceptions(err):
    print("RejectedRecords: ", err)
    for rr in err.response["RejectedRecords"]:
        print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        if "ExistingVersion" in rr:
            print("Rejected record existing version: ", rr["ExistingVersion"])


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
qx.App.run()
