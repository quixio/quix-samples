from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models import ParameterData, StreamEndType
from quixstreaming.app import App
import time
import datetime
import os

properties = {
    "acks": "0"
}

client = QuixStreamingClient(properties=properties)

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")
input_topic = client.open_input_topic(os.environ["input"], "default-consumer-group")
output_topic = client.open_output_topic(os.environ["output"])


# Callback called for each incoming stream
def read_stream(new_stream: StreamReader):
    # Create a new stream to output data
    stream_writer = output_topic.create_stream(new_stream.stream_id + "-car-game-input")

    stream_writer.properties.parents.append(new_stream.stream_id)

    stream_writer.parameters.add_definition("throttle").set_range(0.0, 1.0)
    stream_writer.parameters.add_definition("brake").set_range(0.0, 1.0)
    stream_writer.parameters.add_definition("steering").set_range(-1.0, 1.0)
    last_time = time.time_ns()

    # Callback triggered for each new data frame
    def on_parameter_data_handler(data: ParameterData):
        nonlocal last_time
        print(time.time_ns() - last_time)
        last_time = time.time_ns()
        
        for row in data.timestamps:
            y_grav = row.parameters["Y_grav"].numeric_value

            receivedThrottle = row.parameters["throttle"].numeric_value
            receivedBrake = row.parameters["brake"].numeric_value

            # We calculate steering angle from g force data.
            steering = y_grav / 4.5

            data = ParameterData()

            data.add_timestamp(datetime.datetime.utcnow()) \
                .add_tags(row.tags) \
                .add_value("throttle", receivedThrottle) \
                .add_value("oldtimestamp", str(row.timestamp)) \
                .add_value("delta2", (row.timestamp_nanoseconds / 1000000) - int((time.time()) * 1000)) \
                .add_value("brake", receivedBrake) \
                .add_value("steering", steering)

            stream_writer.parameters.write(data)

    # React to new data received from input topic.
    new_stream.parameters.on_read += on_parameter_data_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(end_type: StreamEndType):
        stream_writer.close(end_type)
        print("Stream closed:" + stream_writer.stream_id)

    new_stream.on_stream_closed += on_stream_close

    # React to any metadata changes.
    def stream_properties_changed():
        if new_stream.properties.name is not None:
            stream_writer.properties.name = new_stream.properties.name + " car game input"

    new_stream.properties.on_changed += stream_properties_changed


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")
App.run()
print("Exiting")
