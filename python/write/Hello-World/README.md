# Python Hello World

This is an example on how to connect and start a new stream with some values.



```python
# Create a streaming client
client = QuixStreamingClient("token")

# Open the output topic
output_topic = client.open_output_topic("output")

# Create the stream
stream = output_topic.create_stream()

# Send some values
stream.parameters \
    .buffer \
    .add_timestamp(datetime.datetime.utcnow()) \
    .add_value("ParameterA", math.sin(index / 200.0) + math.sin(index) / 5.0) \
    .write()
time.sleep(0.01)
```


## Local Development

For information on how to set up your local development environment see the readme that's relevant to you [here](../../LocalDevelopment/)

