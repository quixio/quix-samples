import quixstreams as qx
import os
import pandas as pd
import influxdb_client_3 as InfluxDBClient3
import ast
import datetime


client = qx.QuixStreamingClient()

# get the topic consumer for a specific consumer group
topic_consumer = client.get_topic_consumer(topic_id_or_name = os.environ["input"],
                                           consumer_group = "empty-destination")

# Read the environment variable and convert it to a list
tag_columns = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "[]"))

# Read the enviroment variable for measurement name and convert it to a list
measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', os.environ["input"])
                                           
client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])


def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    try:
        # Reformat the dataframe to match the InfluxDB format
        df = df.rename(columns={'timestamp': 'time'})
        df = df.set_index('time')
        df["stream_id"] = stream_consumer.stream_id

        client.write(df, data_frame_measurement_name=measurement_name, data_frame_tag_columns=tag_columns) 

        print(f"{str(datetime.datetime.utcnow())}: Persisted {df.shape[0]} rows.")
    except Exception as e:
        print("{str(datetime.datetime.utcnow())}: Write failed")
        print(e)


def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    
    # Buffer to batch rows every 250ms to reduce CPU overhead.
    buffer = stream_consumer.timeseries.create_buffer()
    buffer.time_span_in_milliseconds = 250
    buffer.buffer_timeout = 250

    buffer.on_dataframe_released = on_dataframe_received_handler


# subscribe to new streams being received
topic_consumer.on_stream_received = on_stream_received_handler

print("Listening to streams. Press CTRL-C to exit.")

# Handle termination signals and provide a graceful exit
qx.App.run()