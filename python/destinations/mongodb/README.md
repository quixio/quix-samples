# MongoDB

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/mongodb) 
demonstrates how to consume data from a Kafka topic in Quix and write the data to a 
MongoDB database using the [Quix Streams MongoDB sink](https://quix.io/docs/quix-streams/connectors/sinks/mongodb-sink.html).

## Using with a Quix Cloud MongoDB Service

This deployment will work seamlessly with a [Quix Cloud MongoDB service](https://github.com/quixio/quix-samples/tree/main/docker/mongodb).

Assign the same `mongodb-connection` variable group to this connector and to the
**Quix Cloud MongoDB service**, and both ends use the same connection - no need to copy
the values by hand:

```shell
MONGO_HOST="mongodb"      # the internal service name
MONGO_PORT="27017"
MONGO_USER="admin"
MONGO_PASSWORD="<YOUR PASSWORD>"
```
## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables (which correspond to the 
`MongoDBSink` parameter names):

### Required
- `input`: The input Kafka topic name
- `MONGO_DATABASE`: MongoDB database name
- `MONGO_COLLECTION`: MongoDB collection name

The connection itself comes from the shared **`mongodb-connection`** Variable Group, so
this sink, the bundled MongoDB service and any other client agree on one connection:

- `MONGO_HOST`: MongoDB host name (Default: `mongodb`)
- `MONGO_PORT`: MongoDB host port (Default: `27017`)
- `MONGO_USER`: MongoDB username (Default: `admin`)
- `MONGO_PASSWORD`: MongoDB password

### Optional
Unless explicitly defined, these are set to the [`MongoDBSink` defaults](https://quix.io/docs/quix-streams/connectors/sinks/mongodb-sink.html#configuration-options).

- `MONGODB_DOCUMENT_MATCHER`: How documents are selected to update.    
    Accepts a JSON-serializable string formatted as a MongoDB filter Query.    
    Can handle kafka message refs using `__{ref}` with dot notation for nested fields.  
    ex: `'{"_id": "__key", "first_name": "__value.name.first"}'`    
    Possible refs: key, value, headers, timestamp, topic, partition, offset.    
    **Default**: '{"_id": "__key"}'.
- `MONGODB_UPSERT`: Boolean to create documents if no matches with `MONGODB_DOCUMENT_MATCHER`.    
    **Default**: "true"
- `MONGODB_UPDATE_METHOD`: How documents found with `MONGODB_DOCUMENT_MATCHER` are updated.    
    'Update*' options will only update fields included in the kafka message.    
    'Replace*' option fully replaces the document with the contents of kafka message.    
    - "UpdateOne": Updates the first matching document (usually based on `_id`).    
    - "UpdateMany": Updates ALL matching documents (usually NOT based on `_id`).    
    - "ReplaceOne": Replaces the first matching document (usually based on `_id`).    
    **Default**: "UpdateOne".
- `MONGODB_ADD_MESSAGE_METADATA`: Boolean to include key, timestamp, and headers as `__{field}`    
    **Default**: "false"
- `MONGODB_ADD_TOPIC_METADATA`: Boolean to include topic, partition, and offset as `__{field}`    
    **Default**: "false"


## Requirements / Prerequisites

You will need to have a MongoDB instance with access to a db and collection.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
