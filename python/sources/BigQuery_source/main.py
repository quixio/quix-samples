# import the Quix Streams modules for interacting with Kafka:
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext

# import additional modules as needed
import os
import json
import time as tm
import base64
import random
import pandas as pd
from decimal import Decimal
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, date, timezone, time
from typing import Dict, Any, List, Generator, Optional



# for local dev, load env vars from a .env file
from dotenv import load_dotenv

load_dotenv()


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles all BigQuery data types"""
    
    def default(self, obj):
        # Handle pandas NA type explicitly
        if isinstance(obj, pd._libs.missing.NAType):
            return None
            
        # Handle datetime.time objects
        if isinstance(obj, datetime.time):
            return obj.isoformat()
            
        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()
            
        # Handle date objects
        if isinstance(obj, date):
            return obj.isoformat()
            
        # Handle Decimal objects
        if isinstance(obj, Decimal):
            return str(obj)
            
        # Handle bytes
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
            
        # Handle NaN and NA values
        if pd.isna(obj):
            return None
            
        # Let the base class handle anything else
        return super().default(obj)


class BigQuerySerializer(JSONSerializer):
    """Serializer for BigQuery data that handles all data types"""
    
    def __call__(self, value, ctx):
        """Serialize a value to JSON string"""
        if value is None:
            return None
        return self._dumps(value)
        
    def _dumps(self, value):
        # For dictionaries, pre-process to explicitly handle problematic types
        if isinstance(value, dict):
            processed_dict = {}
            for k, v in value.items():
                # Handle pandas NA type explicitly
                if isinstance(v, pd._libs.missing.NAType):
                    processed_dict[k] = None
                # Handle NaT strings
                elif v == 'NaT':
                    processed_dict[k] = None
                else:
                    processed_dict[k] = v
            
            # Use our custom encoder to handle all other special types
            return json.dumps(processed_dict, cls=CustomJSONEncoder)
        
        # Use our custom encoder for any value
        return json.dumps(value, cls=CustomJSONEncoder)


app = Application(consumer_group="data_source", auto_create_topics=True)
serializer = BigQuerySerializer()

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

# define the topic storing the service account credentials and extract the secret value
service_account_json = os.environ["service_account"]
service_account_info = json.loads(service_account_json, strict=False)


def read_data():
    # Connect to BigQuery
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # Query to fetch data from BigQuery with all supported data types
    # This query should include all BQ data types you want to support
    query = """
    Enter your Query here
    """
    
    # Adjusted query to match existing table schema
    # Add other columns only if they exist in your table

    print("Table Rows loading.")
    df = client.query_and_wait(query).to_dataframe()
    print("Table Rows loaded.")

    row_count = len(df)
    stream_id = f"BQ_DATA_{str(random.randint(1, 100)).zfill(3)}"
    headers = df.columns.tolist()

    print(f"Publishing {row_count} rows.")

    for _, row in df.iterrows():
        # Convert row to dictionary while properly handling all data types
        row_data = {}
        for header in headers:
            value = row[header]
            
            # Skip columns that don't exist in the query result
            if pd.isna(value) and header not in df.columns:
                continue
                
            # Handle special data types
            if isinstance(value, (datetime, date)):
                row_data[header] = value.isoformat()
            elif isinstance(value, time):  # Handle datetime.time here
                row_data[header] = value.strftime("%H:%M:%S")  # Convert time to string
            elif isinstance(value, bytes):
                row_data[header] = base64.b64encode(value).decode('utf-8')
            elif isinstance(value, Decimal):
                # Store Decimal as string to preserve precision
                row_data[header] = str(value)
            else:
                row_data[header] = value

        # add current timestamp
        row_data["Timestamp"] = tm.time_ns()
        yield stream_id, row_data


def main():
    """
    Read data from the BigQuery table and publish it to Kafka
    """

    def debug_type(obj):
        print(f"Type: {type(obj)}, Value: {obj}, repr: {repr(obj)}")
        if hasattr(obj, '__dict__'):
            print(f"Object attributes: {obj.__dict__}")
        return str(obj)

    producer = app.get_producer()

    with producer:
        for message_key, row_data in read_data():
            try:
                serialized_value = serializer(
                    value=row_data,
                    ctx=SerializationContext(topic=topic.name, field='value')
                )

                producer.produce(
                    topic=topic.name,
                    key=message_key,
                    value=serialized_value,
                )
            except Exception as e:
                print(f"Error serializing row: {e}")
                print(f"Problematic row data: {row_data}")
                for k, v in row_data.items():
                    print(f"Key: {k}, Value type: {type(v)}")
                    if pd.isna(v):
                        print(f"  This is a pandas NA value: {repr(v)}")
                # Continue with next row instead of stopping completely
                continue
                
        print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
    except Exception as e:
        print(f"Error: {e}")