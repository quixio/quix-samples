from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
import os
import json
from setup_logger import logger

# BigQuery Constants
PROJECT_ID = os.environ["PROJECT_ID"]
DATASET_ID = os.environ["DATASET_ID"]
DATASET_LOCATION = os.environ["DATASET_LOCATION"]
SERVICE_ACCOUNT_JSON = os.environ["SERVICE_ACCOUNT_JSON"]

class Null:
    def __init__(self):
        self.name = 'NULL'

    def __str__(self):
        return self.name

def dataset_exists(client, dataset_id: str):
    try:
        client.get_dataset(dataset_id)
        logger.debug("Dataset {} already exists".format(dataset_id))
        return True
    except NotFound:
        logger.debug("Dataset {} is not found".format(dataset_id))
        return False

def create_dataset(client):
    dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
    if not dataset_exists(client, dataset_id):
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = DATASET_LOCATION
        dataset = client.create_dataset(dataset, timeout = 30)
        logger.debug("Created dataset {}.{}".format(client.project, dataset.dataset_id))

def connect_bigquery():
    service_account_info = json.loads(SERVICE_ACCOUNT_JSON, strict = False)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = bigquery.Client(credentials = credentials, project = credentials.project_id,)
    create_dataset(client)
    return client


def table_exists(client, table_id: str):
    try:
        client.get_table(table_id)
        logger.debug("Table {} already exists.".format(table_id))
        return True
    except NotFound:
        logger.debug("Table {} is not found.".format(table_id))
        return False 


def create_table(client, table_name: str, schema: list):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    if not table_exists(client, table_id):
        table = bigquery.Table(table_id, schema = schema)
        table = client.create_table(table)
        logger.debug(
            "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
        )

def create_paramdata_table(client, table_name: str):
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode = "REQUIRED"),
        bigquery.SchemaField("stream_id", "STRING", mode = "REQUIRED"),
    ]
    create_table(client, table_name, schema)


def create_metadata_table(client, table_name: str):
    schema = [
        bigquery.SchemaField("stream_id", "STRING", mode = "REQUIRED")
    ]
    create_table(client, table_name, schema)

def create_eventdata_table(client, table_name: str):
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode = "REQUIRED"),
        bigquery.SchemaField("stream_id", "STRING", mode = "REQUIRED"),
        bigquery.SchemaField("value", "STRING", mode = "REQUIRED"),
        bigquery.SchemaField("event_id", "STRING", mode = "REQUIRED"),
    ]
    create_table(client, table_name, schema)


def create_parents_table(client, table_name: str):
    schema = [
        bigquery.SchemaField("stream_id", "STRING", mode = "REQUIRED"),
        bigquery.SchemaField("parent_id", "STRING", mode = "REQUIRED"),
    ]
    create_table(client, table_name, schema)


def create_properties_table(client, table_name: str):
    schema = [
        bigquery.SchemaField("stream_id", "STRING", mode = "REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode = "NULLABLE"),
        bigquery.SchemaField("location", "STRING", mode = "NULLABLE"),
        bigquery.SchemaField("topic", "STRING", mode = "NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode = "NULLABLE"),
        bigquery.SchemaField("data_start", "NUMERIC", mode = "NULLABLE"),
        bigquery.SchemaField("data_end", "NUMERIC", mode = "NULLABLE"),
    ]
    create_table(client, table_name, schema)

def column_exists(schema, column_name: str):
    fields = []
    for field in schema:
        fields.append(field.name)
    if column_name in fields:
        return True
    else:
        return False

def create_column(client, table_name: str, column_name: str, col_type: str):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table = client.get_table(table_id)
    original_schema = table.schema

    if col_type == 'NUMERIC':
        col_type = 'FLOAT64'
    
    if not column_exists(original_schema, column_name):

        new_schema = original_schema[:]
        new_schema.append(bigquery.SchemaField(column_name, col_type))
        table.schema = new_schema
        table = client.update_table(table, ["schema"])

        if len(table.schema) == len(original_schema) + 1 == len(new_schema):
            logger.debug("A new column has been added.")
        else:
            logger.error("The column has not been added.")


def insert_row(client, table_name: str, cols: list, vals: list):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    rows_to_insert = []
    for val in vals:
        for i in range(len(val)):
            if type(val[i]) == Null:
                val[i] = None
        row = dict(zip(cols, val))
        rows_to_insert.append(row)

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors == []:
        logger.debug("New rows have been added.")
    else:
        logger.error("Encountered errors while inserting rows: {}".format(errors))


def delete_row(client, table_name: str, condition: str):
    pass