import time
import boto3
import os


class KinesisFunctions:
    run = True
    is_connected = False
    kinesis_client = None

    def __init__(self, quix_stream, data_handler):
        self.quix_stream = quix_stream
        self.data_handler = data_handler

    def stop_running(self):
        self.run = False

    def connect(self):
        # connect to aws kinesis using a boto3 client
        self.kinesis_client = boto3.client(
            'kinesis',
            aws_access_key_id = os.environ["aws_access_key_id"],
            aws_secret_access_key = os.environ["aws_secret_access_key"],
            region_name = os.environ["aws_region_name"]
        )

    def get_data(self):

        # set up the shard iterator
        si = self.kinesis_client.get_shard_iterator(
            StreamName = os.environ["aws_stream_name"],
            ShardId='shardId-000000000000',
            ShardIteratorType='LATEST'
        )

        shard_iterator = si["ShardIterator"]

        # print CONNECTED! so that the Quix Portal
        # knows and can nav to the next page
        # only do it once
        if not self.is_connected:
            print("CONNECTED!")
            self.is_connected = True

        # run until stop_running is called
        while self.run:
            # use the shard iterator to get the next record
            record_data = self.kinesis_client.get_records(ShardIterator = shard_iterator)
            shard_iterator = record_data["NextShardIterator"]

            # if there is a record
            if len(record_data["Records"]) > 0:

                # iterate the records
                for r in record_data["Records"]:
                    # get the data
                    d = r["Data"]

                    # decode and/or pass the passed in data to the data handler
                    if isinstance(d, bytes):
                        self.data_handler(d.decode())
                    else:
                        self.data_handler(d)

            # adjust the sleep time depending on how far behind we are
            behind = record_data["MillisBehindLatest"]
            if behind < 1000:
                time.sleep(1)
            else:
                time.sleep(0.1)
