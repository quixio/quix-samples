# Redis Server

This sample demonstrates how to run a Redis cache in your Quix Cloud pipeline.

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

For more configuration options and details, refer to [Redis Docker Hub](https://hub.docker.com/_/redis).

## How to use

Use this `Python` code to communicate with and test your Redis server.

`NOTE: Run this from within Quix Cloud in the same project where your Redis server is deployed.`

Add `redis` to the requirements.txt file then use the following code to access Redis.

```
import redis

# Connect to Redis
client = redis.Redis(host='redis', port=6379, db=0)

# Save a key-value pair
client.set('my_key', 'Hello, Redis!')

# Read the value back
value = client.get('my_key')

# Since Redis returns bytes, decode to string if necessary
if value:
    value = value.decode('utf-8')

print(f"The value of 'my_key' is: {value}")
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Redis and is offered as-is, with no Redis specific support from Quix.