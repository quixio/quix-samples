import quixstreams as qx
import os, time
from datetime import datetime, timedelta
from pytz import timezone
from enum import Enum
from threading import Lock, Thread
import gzip
import boto3

headers = ["timestamp"]

# keep the main loop running
run = True

# comma separated list of parameters that contains formatted data to save to s3
param_csv = os.environ["parameters"]
# split and trim the entries
params_to_write = [x.strip() for x in param_csv.split(',')]
headers += params_to_write

bucket = os.environ["s3_bucket"]
s3_folder = os.environ["s3_folder"]
# if set to true, new folders will be created in s3 for each stream using stream id as name 
s3_folder_per_stream = os.environ["s3_folder_per_stream"].lower() == "true"

client = qx.QuixStreamingClient()
commit_settings = qx.models.CommitOptions()
commit_settings.auto_commit_enabled = False
topic = client.get_topic_consumer(os.environ["input"], "s3-sink", 
                                  commit_settings = commit_settings, auto_offset_reset = qx.AutoOffsetReset.Latest)

# files created in s3 will have this prefix
prefix = os.environ["prefix"]
# files created in s3 will have this suffix (intended for file extensions)
suffix = os.environ["suffix"]

mutex = Lock()
tz = tz = timezone(os.environ["timezone"])

# maximum number of messages to wait for before uploading files to s3. 
max_count = int(os.environ["batch_msg_count"])
# maximum time interval to wait before an upload happens.
max_interval = timedelta(seconds = int(os.environ["batch_time_interval"]))

class Batch:
    def __init__(self, count, start, fname):
        self.count = count
        self.start = start
        self.fname = fname

# if batch mode is set to NONE, max_count and max_interval is ignored. When a message is received, parameter data
# is written to a file and uploaded immediately.
# if the batch mode is set to TIME, parameter data is written to a file for a period specified by max_interval before
# uploading the file to s3.
# if the batch mode is set to COUNT, parameter data in max_count number of messages is written to a file before
# uploading to s3. For this count to be accurate, each message must only contain data for one timestamp.
# if batch mode is set to TIME_OR_COUNT, parameter data is written to file until the max_interval or max_count is reached
# (whichever comes first) before uploading to s3.
BatchMode = Enum("BatchMode", "NONE TIME COUNT TIME_OR_COUNT")
batch_mode = BatchMode.NONE
if max_count > 0 and max_interval.total_seconds() > 0:
    batch_mode = BatchMode.TIME_OR_COUNT
    print(f"Files will be uploaded approx. every {max_interval.total_seconds()} seconds or {max_count} records. Whichever is soonest.")
elif max_count > 0:
    batch_mode = BatchMode.COUNT
    print(f"Files will be uploaded every {max_count} records")
elif max_interval.total_seconds() > 0:
    batch_mode = BatchMode.TIME
    print(f"Files will be uploaded approx. every {max_interval.total_seconds()} seconds.")
else:
    batch_mode = BatchMode.NONE
    print("Files will be uploaded for every record. Time and Count parameters will be ignored.")

batches = {}

s3 = boto3.client(
    "s3",
    aws_access_key_id = os.environ["aws_access_key_id"],
    aws_secret_access_key = os.environ["aws_access_key"]
)

def upload(stream_id: str, fname: str):
    if os.path.exists(fname):
        try:
            if s3_folder:
                if s3_folder_per_stream:
                    path = "/".join([s3_folder, stream_id, fname])
                else:
                    path = "/".join([s3_folder, fname])
            else:
                if s3_folder_per_stream:
                    path = "/".join([stream_id, fname])
                else:
                    path = fname
            s3.upload_file(fname, bucket, path)
            topic.commit()
        except Exception as e:
            print("Error: upload(): " + str(e))
        finally:
            os.remove(fname)
            headers_written_for_file.remove(fname)
    else:
        print("Error: file " + fname + " not found")

def is_new_batch(batch: Batch):
    now = datetime.now()
    start = batch.start
    interval = now - start
    if batch_mode == BatchMode.NONE:
        return True
    if batch_mode == BatchMode.TIME:
        return interval >= max_interval
    if batch_mode == BatchMode.COUNT:
        return batch.count >= max_count
    if batch_mode == BatchMode.TIME_OR_COUNT:
        return interval >= max_interval or batch.count >= max_count
    raise Exception("Unknown batch mode")


# modify this function, if you prefer a different file naming logic.
def file_name(start: datetime):
    return prefix + start.astimezone(tz).isoformat(timespec='milliseconds').replace(":", "").replace("+", "_plus_") + suffix + ".gz"

headers_written_for_file = []

def save(stream_id: str, data: qx.TimeseriesData):
    global batches
    if data is not None and len(data.timestamps) > 0:
        mutex.acquire()
        try:
            if stream_id in batches:
                batch = batches[stream_id]
                if len(data.timestamps) > 1 and (batch_mode == BatchMode.COUNT or batch_mode == BatchMode.TIME_OR_COUNT):
                    print("Warn: data contains more than one timestamp: batch size may not be accurate")
                with gzip.open(batch.fname, "at") as fd:
                    output_data = ""
                    for ts in data.timestamps:
                        output_rows = ""

                        for f in params_to_write:
                            comma = ""
                            if output_rows != "":
                                comma = ","

                            if f in ts.parameters.keys():
                                if ts.parameters[f].string_value is not None:
                                    output_rows += f"{comma}{ts.parameters[f].string_value}"
                                elif ts.parameters[f].numeric_value is not None:
                                    output_rows += f"{comma}{ts.parameters[f].numeric_value}"
                                else:
                                    output_rows += f"{comma}{0}"
                            else:
                                output_rows += f"{comma}{0}"

                        output_rows += "\n"
                        output_rows = f"{ts.timestamp_nanoseconds},{output_rows}"
                        output_data += output_rows

                    if output_data != "":
                        if batch.fname not in headers_written_for_file:
                            fd.write(",".join(headers))
                            fd.write("\n")
                            headers_written_for_file.append(batch.fname)

                        batch.count += 1
                        fd.write(output_data)

                if is_new_batch(batch):
                    if batch.count > 0:
                        upload(stream_id, batch.fname)
                        print("Info: save() uploaded batch " + batch.fname + " with " + str(batch.count) + " records to S3")
                    start = datetime.now()
                    fname = file_name(start)
                    batches[stream_id] = Batch(0, start, fname)
            else:
                print("Error: stream " + stream_id + " not found in batches")
        finally:
            mutex.release()

def stream_received_handler(stream: qx.StreamConsumer):
    global batches

    def read_handler(stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
        save(stream.stream_id, data)
    
    def stream_closed_handler(stream_consumer: qx.StreamConsumer, status: qx.StreamEndType):
        batch = batches.pop(stream.stream_id, None)
        if batch is not None and batch.count > 0:
            upload(stream.stream_id, batch.fname)
            print("Info: stream_closed_handler() uploaded batch " + batch.fname + " with " + str(batch.count) + " records to S3")
        print("Info: stream " + stream.stream_id +  "closed: " + str(status))

    print("Info: new stream: " + stream.stream_id)
    start = datetime.now()
    fname = file_name(start)
    batches[stream.stream_id] = Batch(0, start, fname)
    stream.timeseries.on_data_received = read_handler
    stream.on_stream_closed = stream_closed_handler

topic.on_stream_received = stream_received_handler

def job():
    while run:
        print("Debug: started batch job at " + str(datetime.now()))
        mutex.acquire()
        try:
            for key in batches.keys():
                now = datetime.now()
                batch = batches[key]
                if is_new_batch(batch):
                    if batch.count > 0:
                        upload(key, batch.fname)
                        print("Info: job() uploaded batch " + batch.fname + " with " + str(batch.count) + " records to S3")
                    fname = file_name(now)
                    batches[key] = Batch(0, now, fname)
        finally:
            mutex.release()
        interval = max_interval.total_seconds() / 2
        print("Debug: scheduled next batch job to run at " + str(datetime.now() + timedelta(seconds = interval)))
        time.sleep(interval)

thread = None
if batch_mode == BatchMode.TIME or batch_mode == BatchMode.TIME_OR_COUNT:
    thread = Thread(target = job)  
    thread.start()
    print("Info: started batch scheduler")

print("Listening to streams. Press CTRL-C to exit.")

def before_shutdown():
    global run
    run = False

# Handle graceful exit
qx.App.run(before_shutdown=before_shutdown)