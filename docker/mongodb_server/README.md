# MongoDB Server

This sample demonstrates how to run a MongoDB instance in your Quix Cloud pipeline.

> **NOTE**: This implementation is largely for development purposes...please see
> [limitations](#limitations) before continuing.

## How to Run/Deploy

1. Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account (or log in) 
2. Find the `MongoDB Server` Code Template to use this project

Then, either:

- (Easiest) Click `Deploy` and provide a name; the server will be instantly deployed!


OR

- (More Setup) Click `Preview Code` + `Save to your repo`, which forks the project to your own Git repo for additional customization.
  - Here you can edit any of the docker or config files, along with the deployment `YAML` in the upper-right corner
  - After doing additional configuration, `Commit` and `Sync` your changes.
  - Click `Deploy` to deploy the container.


## Connecting a Client

You can connect with a Mongo client using the url format: 

- `mongodb://{host}:{port}`

### Default Hostname and Port

By default, the mongo instance can be connected to via `mongodb://mongodb:27017`. 

### Changing Hostname and Port

The hostname and port correspond to the `service name` and `port` under the `NETWORK SETTINGS` 
header when finalizing a new deployment (`Deployment` button) of the service. 

You can similarly find these values in the deployment `YAML` button in the upper right corner, under:

- `deployments` -> `{deployment name}` -> `network` -> `serviceName`, `ports`

### Example Use with Quix MongoDBSink

> **NOTE:** requires `pip install quixstreams[mongodb]`

Here is a simple example that dumps a topic into your new MongoDB instance:

```python
from quixstreams import Application
from quixstreams.sinks.community.mongodb import MongoDBSink
from os import environ

app = Application(consumer_group="my_group", auto_offset_reset="earliest")
df = app.dataframe(topic=app.topic(name=environ['input']))
df.sink(MongoDBSink(
    url=f"mongodb://mongodb:27017",
    db="test_db",
    collection="test_collection",
    update_method="UpdateOne",
    upsert=True,
))
```

#### More info on Connectors
You can see the [MongoDBSink documentation](https://quix.io/docs/quix-streams/connectors/sinks/mongodb-sink.html) 
for more info on its capabilities.

Or, for a pure no-code implementation of it, try out the corresponding
[MongoDB connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/mongodb)!

## Limitations

### Data Persistence

We currently do not support users being able to
set up a persistent MongoDB themselves.

this means **all data will be lost upon container stops or restarts**.

If you need data persistence, please get in touch with us so we can assist you!

## Setting up Credentials/Authentication:

1. add the following environment variables to the deployment:

   - `MONGO_INITDB_ROOT_USERNAME`
   - `MONGO_INITDB_ROOT_PASSWORD` (as a secret)

2. add the `"--auth"` to the dockerfile `CMD` line.

3. Now when connecting with a client, the url format will be:

   - `mongodb://{username}:{password}@{hostname}:{port}`



## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
