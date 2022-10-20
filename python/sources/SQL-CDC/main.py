from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quixstreaming.state.localfilestorage import LocalFileStorage
import time
from datetime import datetime
import os
import pyodbc
import pandas as pd
import threading
import helper_functions

last_modified_storage_key = "LAST_MODIFIED"

config = helper_functions.load_config()
table_name = config["table_name"]

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()
storage = LocalFileStorage()

# Open the output topic where to write data out
output_topic = client.open_output_topic(os.environ["output"])
stream = output_topic.create_stream(table_name)

print("connecting...")
conn = pyodbc.connect("Driver={0};Server={1};UID={2};PWD={3};Database={4};TrustServerCertificate=yes;"
                .format(config["driver"], config["server"], config["user_id"], config["password"], config["database"]))
print("CONNECTED!")

poll_for_data = True

offset = None
if storage.containsKey(last_modified_storage_key):
    stored_value = storage.get(last_modified_storage_key)
    offset = datetime.strptime(stored_value, "%Y-%m-%d %H:%M:%S")
else:
    if config["use_utc"]:
        offset = datetime.utcnow()
    else:
        offset = datetime.now()
    offset = offset - config["time_delta"]
    offset = offset.strftime("%Y-%m-%d %H:%M:%S")


def data_poller_thread():
    global offset
    while poll_for_data:
        print("Looking for data newer than: {}".format(offset))

        start_time = time.time()

        if not helper_functions.check_table_exists(conn, table_name):
            raise Exception("A table called '{}' was not found in the database".format(table_name))

        sql = "SELECT * FROM {0} WHERE {2} > '{1}' ORDER By {2} DESC".format(table_name,
                                                                             offset,
                                                                             config["last_modified_column"])

        # fetch the data
        data = pd.read_sql(sql, conn)

        # add timestamp for quix
        data[config["last_modified_column"]] = pd.to_datetime(data[config["last_modified_column"]])
        data = data.rename(columns={config["last_modified_column"]: 'timestamp'})

        # print(sql)
        # print(data)

        if data.empty:
            print("No new data found, waiting for {} seconds".format(config["poll_interval"]))
            time.sleep(config["poll_interval"])
            continue

        # print(data.columns)

        # remove columns
        if config["drop_cols"] != "":
            data = helper_functions.drop_columns(conn, config["drop_cols"].split(","), data, table_name)

        # rename columns
        if config["rename_cols"] is not None:
            data = helper_functions.rename_columns(conn, config["rename_cols"], data, table_name)

        print("Loaded {} rows in {}".format(len(data.index), str(time.time() - start_time)))
        start_time = time.time()
        stream.parameters.write(data)
        print("Sent {} rows in {}".format(len(data.index), str(time.time() - start_time)))

        # lastly: set the last modified key in storage in case of a restart
        # update the offset with the newest datetime from the db
        offset = data[config["last_modified_column"]][0]
        storage.set(last_modified_storage_key, str(offset))

        time.sleep(config["poll_interval"])


def before_shutdown():
    global poll_for_data
    poll_for_data = False


thread = threading.Thread(target=data_poller_thread)
thread.start()

# start the app, ensure topics exist and thread handle abort sequence
App.run(before_shutdown=before_shutdown)
