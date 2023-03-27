import quixstreams as qx
import time
import datetime
import os

properties = {
    "acks": "0"
}

client = qx.QuixStreamingClient(properties = properties)

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group")
producer_topic = client.get_topic_producer(os.environ["output"])


# Callback called for each incoming stream
def read_stream(new_stream: qx.StreamConsumer):
    # Create a new stream to output data
    stream_producer = producer_topic.create_stream(new_stream.stream_id + "-car-game-input")

    stream_producer.properties.parents.append(new_stream.stream_id)

    stream_producer.timeseries.add_definition("throttle").set_range(0.0, 1.0)
    stream_producer.timeseries.add_definition("brake").set_range(0.0, 1.0)
    stream_producer.timeseries.add_definition("steering").set_range(-1.0, 1.0)
    last_time = time.time_ns()

    # Callback triggered for each new data frame
    def on_data_handler(stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
        nonlocal last_time
        print(time.time_ns() - last_time)
        last_time = time.time_ns()
        
        for row in data.timestamps:
            y_grav = row.parameters["Y_grav"].numeric_value

            receivedThrottle = row.parameters["throttle"].numeric_value
            receivedBrake = row.parameters["brake"].numeric_value

            # We calculate steering angle from g force data.
            steering = y_grav / 4.5

            data = qx.TimeseriesData()

            data.add_timestamp(datetime.datetime.utcnow()) \
                .add_tags(row.tags) \
                .add_value("throttle", receivedThrottle) \
                .add_value("oldtimestamp", str(row.timestamp)) \
                .add_value("delta2", (row.timestamp_nanoseconds / 1000000) - int((time.time()) * 1000)) \
                .add_value("brake", receivedBrake) \
                .add_value("steering", steering)

            stream_producer.timeseries.publish(data)

    # React to new data received from input topic.
    new_stream.timeseries.on_data_received += on_data_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(stream_consumer: qx.StreamConsumer, end_type: qx.StreamEndType):
        stream_producer.close(end_type)
        print("Stream closed:" + stream_producer.stream_id)

    new_stream.on_stream_closed = on_stream_close

    # React to any metadata changes.
    def stream_properties_changed():
        if new_stream.properties.name is not None:
            stream_producer.properties.name = new_stream.properties.name + " car game input"

    new_stream.properties.on_changed = stream_properties_changed


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()
print("Exiting")
