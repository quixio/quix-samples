from quixstreaming import QuixStreamingClient, StreamReader, ParameterData, AutoOffsetReset, CommitOptions, StreamEndType
from quixstreaming.app import App
import os
from datetime import datetime, timedelta
from pytz import timezone
from enum import Enum
from threading import Lock, Timer
import gzip
import boto3

client = QuixStreamingClient()
commit_settings = CommitOptions()
commit_settings.auto_commit_enabled = False
topic = client.open_input_topic(os.environ["input"], "s3-sink", commit_settings=commit_settings, auto_offset_reset=AutoOffsetReset.Latest)

param = os.environ["parameter"]
bucket = os.environ["s3_bucket"]
s3_folder = os.environ["s3_folder"]
s3_folder_per_stream = os.environ["s3_folder_per_stream"].lower() == "true"
prefix = os.environ["prefix"]
suffix = os.environ["suffix"]

mutex = Lock()
tz = tz = timezone("Asia/Singapore")
max_count = int(os.environ["batch_msg_count"])
max_interval = timedelta(seconds=int(os.environ["batch_time_interval"]))

class Batch:
    def __init__(self, count, start, fname):
        self.count = count
        self.start = start
        self.fname = fname

BatchMode = Enum("BatchMode", "NONE TIME COUNT TIME_OR_COUNT")
batch_mode = BatchMode.NONE
if max_count > 0 and max_interval.total_seconds() > 0:
    batch_mode = BatchMode.TIME_OR_COUNT
elif max_count > 0:
    batch_mode = BatchMode.COUNT
elif max_interval.total_seconds() > 0:
    batch_mode = BatchMode.TIME
else:
    batch_mode = BatchMode.NONE
batches = {}

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ["aws_access_key_id"],
    aws_secret_access_key=os.environ["aws_access_key"]
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
    else:
        print("Error: file " + fname + " not found")

def is_new_batch(batch: Batch):
    now = datetime.now()
    start = batch.start
    interval = now - start
    if batch_mode == BatchMode.NONE:
        return True
    if batch_mode == BatchMode.TIME:
        return interval >= max_interval;
    if batch_mode == BatchMode.COUNT:
        return batch.count >= max_count
    if batch_mode == BatchMode.TIME_OR_COUNT:
        return interval >= max_interval or batch.count >= max_count
    raise Exception("Unknown batch mode")

def file_name(start: datetime):
    return prefix + start.astimezone(tz).isoformat(timespec='milliseconds').replace(":", "").replace("+", "_plus_") + suffix + ".gz"

def save(stream_id: str, data: ParameterData):
    global batches
    if data is not None and len(data.timestamps) > 0:
        mutex.acquire()
        try:
            if stream_id in batches:
                batch = batches[stream_id]
                if len(data.timestamps) > 1 and (batch_mode == BatchMode.COUNT or batch_mode == BatchMode.TIME_OR_COUNT):
                    print("Warn: data contains more than one timestamp: batch size may not be accurate")
                with gzip.open(batch.fname, "at") as fd:
                    for ts in data.timestamps:
                        if ts.parameters[param].string_value is not None:
                            fd.write(ts.parameters[param].string_value)
                            fd.write('\n')
                            batch.count += 1
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

def stream_received_handler(stream: StreamReader):
    global batches

    def read_handler(data: ParameterData):
        save(stream.stream_id, data)
    
    def stream_closed_handler(status: StreamEndType):
        batch = batches.pop(stream.stream_id, None)
        if batch is not None and batch.count > 0:
            upload(stream.stream_id, batch.fname)
            print("Info: stream_closed_handler() uploaded batch " + batch.fname + " with " + str(batch.count) + " records to S3")
        print("Info: stream " + stream.stream_id +  "closed: " + str(status))

    print("Info: new stream: " + stream.stream_id)
    start = datetime.now()
    fname = file_name(start)
    batches[stream.stream_id] = Batch(0, start, fname)
    stream.parameters.on_read += read_handler
    stream.on_stream_closed += stream_closed_handler

topic.on_stream_received += stream_received_handler

def job():
    print("Info: started batch job at " + str(datetime.now()))
    for key in batches.keys():
        mutex.acquire()
        try:
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
    timer = Timer(interval, job)
    timer.daemon = True
    timer.start()
    print("Info: scheduled next batch job to run at " + str(datetime.now() + timedelta(seconds=interval)))

if batch_mode == BatchMode.TIME or batch_mode == BatchMode.TIME_OR_COUNT:
    job()
    print("Info: started batch scheduler")

print("Listening to streams. Press CTRL-C to exit.")
App.run()