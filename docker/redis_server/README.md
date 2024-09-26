# Redis Server

This sample demonstrates how to run a Redis cache in your Quix Cloud pipeline.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.


After deploying the redis cache to your pipeline please edit the pipeline YAML to add network configuration:

 - Click the `YAML` button in the top right of the pipeline view.
 - Click `Edit code` near the top right of the displayed YAML code.
 - Locate the `deployments` section of the YAML.
 - Locate the 'redis' deployment. e.g. look for `- name: redis`
 - Add the following snippet under `resources`
 - Note: `network` should be at the same depth as `resources`.
 - Save the YAML.
 - Click the blue `Sync environment` button.
 - Cllck `Sync to this commit` on the popup.
 
Your updated configuration will be aplied to the redis service and it will be restarted. You can now test the deployment.

[A short video showing the process is available here.](https://youtu.be/bZIwPWhR0iU)

[See the full process of selecting, deploying and configuring your Redis cache service here](https://youtu.be/iP1xDQyNqd4)

```
    network:
      serviceName: redis
      ports:
        - port: 6379
          targetPort: 6379
```

The completed deployment entry for redis should look similar to this:

```
deployments:
  - name: redis
    application: redis
    version: latest
    deploymentType: Service
    resources:
      cpu: 200
      memory: 500
      replicas: 1
    network:
      serviceName: redis
      ports:
        - port: 6379
          targetPort: 6379
```

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

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
