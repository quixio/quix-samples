from quixstreams import Application
from quixstreams.models.serializers.quix import JSONDeserializer
import os
import influxdb_client_3 as InfluxDBClient3
import ast
import datetime
import pandas as pd

app = Application.Quix(consumer_group="influx-destination",
                       auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

# Read the environment variable and convert it to a list
tag_columns = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "[]"))

# Read the environment variable for measurement name and convert it to a list
measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', os.environ["input"])
                                           
client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

def send_data_to_influx(row):
    try:
        # Convert the dictionary to a DataFrame
        row_df = pd.DataFrame([row])

        # Reformat the dataframe to match the InfluxDB format
        row_df = row_df.rename(columns={'timestamp': 'time'})
        row_df = row_df.set_index('time')

        client._write_api.write(
            bucket=os.environ["INFLUXDB_DATABASE"], 
            record=row_df, 
            data_frame_measurement_name='conversationstest', 
            data_frame_tag_columns=tag_columns)

        print(f"{str(datetime.datetime.utcnow())}: Persisted {row_df.shape[0]} rows.")
    except Exception as e:
        print(f"{str(datetime.datetime.utcnow())}: Write failed")
        print(e)

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)
