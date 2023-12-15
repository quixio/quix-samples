from quixstreams import Application
from quixstreams.models.serializers.quix import QuixDeserializer

import os
import redis

r = redis.Redis(
    host=os.environ['redis_host'],
    port=int(int(os.environ['redis_port'])),
    password=os.environ['redis_password'],
    username=os.environ['redis_username'] if 'redis_username' in os.environ else None,
    decode_responses=True)

app = Application.Quix(consumer_group="redis-destination")

input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())


def send_data_to_redis(value: dict) -> None:
    print(value)

    tags = value["Tags"]
    timestamp = int(value["Timestamp"] / 1e6)  # nanoseconds to milliseconds

    valid_keys = [x for x in value.keys() if x not in ["Timestamp", "Tags"] and value[x] is not None and (
            isinstance(value[x], float) or isinstance(value[x], int))]

    if len(valid_keys) == 0:
        return

    print(f"Timestamp: {timestamp}, Number of keys: {len(valid_keys)}")
    pipe = r.pipeline()
    for key in valid_keys:
        pipe.ts().add(key=key, timestamp=timestamp, value=value[key], labels=tags)
    pipe.execute()


sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_redis)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)
