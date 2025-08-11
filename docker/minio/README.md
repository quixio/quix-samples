# MongoDB

This sample demonstrates how to deploy and use MongoDB in your pipeline. Please note: this image is provided by MongoDB and is offered as-is, with no specific support from Quix.

## Using with a Quix Cloud MongoDB Connector

This deployment will work seamlessly with the [Quix Cloud MongoDB sink connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/mongodb).

Simply provide the following arguments to the connector, 
where `username` and `password` are the credentials used when 
creating this service: 

```shell
MONGODB_USERNAME="<YOUR USERNAME>"  # (default: "admin")
MONGODB_PASSWORD="<YOUR PASSWORD>"
MONGODB_HOST="mongodb"
MONGODB_PORT="27017"
```

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Fill in the required environment variables for your MongoDB instance.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

For more configuration options and details, refer to [Mongo Docker Hub](https://hub.docker.com/_/mongo).


## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by the [docker community](https://github.com/docker-library/mongo) and is offered as-is, with no MongoDB specific support from Quix.
