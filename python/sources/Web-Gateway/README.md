# Flask Web Gateway

[This project](https://github.com/quixio/quix-samples/tree/main/python/sources/Web-Gateway) is Flask Web API gateway example to ingest data into the topic from any source via HTTP POST request.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

Enable *public access* to be able to call API externally. 

### Calling the API
```javascript
await fetch("https://<YOUR_DNS_PREFIX>.deployments.quix.io/data", {
      headers: {
        "Content-Type": "application/json"
      },
      method: "POST",
      body: JSON.stringify({
        'message': 'Hello world.'
      }),
    })
      .then((res) => res)
```

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for hello world data.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

