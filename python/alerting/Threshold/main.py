from quixstreaming import StreamingClient, ParameterData, StreamEndType, StreamReader
import threading
import signal
import pandas as pd
import time

# Create a client. Client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")
input_topic = client.open_input_topic('{placeholder:input}', "default-consumer-group")
output_topic = client.open_output_topic('{placeholder:output}')


# Callback called for each incoming stream
def read_stream(new_stream: StreamReader):

    # Create a new stream to output data
    stream_writer = output_topic.create_stream(new_stream.stream_id + "-hard-braking")
    
    stream_writer.properties.parents.append(new_stream.stream_id)

    buffer = new_stream.parameters.create_buffer("Brake")
    buffer.time_span_in_milliseconds = 100  # React to 100ms windows of data.

    # Callback triggered for each new data frame
    def on_parameter_data_handler(data: ParameterData):

        df = data.to_panda_frame()  # Input data frame
        output_df = pd.DataFrame()
        output_df["time"] = df["time"]

        output_df["TAG__LapNumber"] = df["TAG__LapNumber"]
        print(df)

        # If braking force applied is more than 50%, we send True.  
        output_df["HardBraking"] = df.apply(lambda row: "True" if row.Brake > 0.5 else "False", axis=1)  

        stream_writer.parameters.buffer.write(output_df)  # Send filtered data to output topic

    # React to new data received from input topic.
    buffer.on_read += on_parameter_data_handler

    # When input stream closes, we close output stream as well. 
    def on_stream_close(endType: StreamEndType):
        stream_writer.close()
        print("Stream closed:" + stream_writer.stream_id)

    new_stream.on_stream_closed += on_stream_close

    # React to any metadata changes.
    def stream_properties_changed():
        stream_writer.properties.name = new_stream.properties.name + " hard braking"

    new_stream.properties.on_changed += stream_properties_changed


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream
input_topic.start_reading()  # initiate read

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Below code is to handle graceful exit of the model.
event = threading.Event() 


def signal_handler(sig, frame):
    # dispose the topic(s) and close the stream(s)
    print('Closing streams...')
    input_topic.dispose()
    output_topic.dispose()

    print('Setting termination flag')
    event.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while not event.is_set():
    time.sleep(1)

print('Exiting')
