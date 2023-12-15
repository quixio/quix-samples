import time
from collections import defaultdict

import os
import quixstreams as qx
import redis
import pandas as pd

r = redis.Redis(
    host=os.environ['redis_host'],
    port=int(int(os.environ['redis_port'])),
    password=os.environ['redis_password'],
    username=os.environ['redis_username'] if 'redis_username' in os.environ else None,
    decode_responses=True)

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input and output topics")
producer_topic = client.get_topic_producer(os.environ["output"])
stream_producer = producer_topic.create_stream()
stream_producer.timeseries.buffer.time_span_in_milliseconds = 1000


# This function is used only to print the information about the keys
def print_info(key_name, key_info):
    print(f"Key: {key_name}")
    print(f"\tTotal samples: {key_info.total_samples}")
    print(f"\tFirst timestamp: {key_info.first_timestamp}")
    print(f"\tLast timestamp: {key_info.last_timestamp}")
    print(f"\tRetention time: {key_info.retention_msecs}ms")
    print(f"\tLabels: {key_info.labels}")
    print(f"\tSource key: {key_info.source_key}")
    print(f"\tRules: {key_info.rules}")


# This is the main function that reads from Redis and publishes to Quix
def get_data():
    # Start from the first timestamp
    first_timestamp = "-"

    while True:
        # Get data from Redis
        data = r.ts().mrange(first_timestamp, "+", filters=["source=quix"], count=100, with_labels=True)

        # If no data, wait and try again
        if len(data) == 0:
            time.sleep(0.5)
            continue

        # Convert data to DataFrame
        data_by_timestamp = defaultdict(dict)

        for sensor in data:
            sensor_name = next(iter(sensor))
            labels = sensor[sensor_name][0]
            samples = sensor[sensor_name][1]

            for ts, value in samples:
                data_by_timestamp[ts][sensor_name] = value

                if first_timestamp == "-" or ts > first_timestamp:
                    first_timestamp = ts + 1

        for data in data_by_timestamp.items():
            print(data)
            df = pd.DataFrame([data[1]])
            df["Timestamp"] = pd.to_datetime(data[0], unit="ms")
            stream_producer.timeseries.publish(df)


def main():
    keys = r.keys()

    for key in keys:
        info = r.ts().info(key)
        print_info(key, info)

    get_data()


if __name__ == "__main__":
    print("Starting application")
    print("Press CTRL-C to exit.")
    main()
