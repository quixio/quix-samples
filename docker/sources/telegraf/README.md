# Telegraf source

This connector uses Telegraf collector with Quix output plugin sending data into Quix topic.

## How to run locally

First build docker container from dockerfile.
```
docker build -t quix-telegraf .
```

then run it with run command:
```
docker run -d --name quix-telegraf 
```

## Environment variables

The code sample uses the following environment variables:

- **Topic**: Name of the output topic to write into.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.