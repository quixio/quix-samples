from quixstreams import Application

import os

import redis


# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

r = redis.Redis(
    host=os.environ['redis_host'],
    port=int(int(os.environ['redis_port'])),
    password=os.environ.get('redis_password'),
    username=os.environ['redis_username'] if 'redis_username' in os.environ else None,
    decode_responses=True)

try:
    r.ping()
    print("CONNECTED!")
except Exception as e:
    print(f"ERROR! Failed to connect to Redis at {os.environ['redis_host']}:{os.environ['redis_port']}: {e}")

redis_key_prefix = os.environ.get('redis_key_prefix', '')

consumer_group = os.getenv("consumer_group_name", "redis-destination")
app = Application(consumer_group=consumer_group)

input_topic = app.topic(os.environ["input"])


created_keys = set()


def send_data_to_redis(value: dict) -> None:
    print(value)

    key = f"{redis_key_prefix}:{value['key']}:{value['m']}"

    if key not in created_keys:
        try:
            r.ts().create(key, labels={"ts": "true"})
        except redis.exceptions.ResponseError:
            r.ts().alter(key, labels={"ts": "true"})
        created_keys.add(key)

    r.ts().add(key, value['time'], value['used_percent'])

    print(f"Data stored in Redis under key: {key}")


sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_redis)

if __name__ == "__main__":
    print("Starting application")
    app.run()
