from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
import os
import pandas as pd 
import time
import signal
from threading import Thread, Event

# should the main loop run?
run = True

DATASET_PATH = "./data/data.csv"

# configure security objects
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])
output_stream = output_topic.create_stream('rawdata-in-stream')

output_stream.properties.name = 'raw_data'
output_stream.properties.location = '/dataset/raw_data'


def get_data():
    quix_functions = QuixFunctions(output_stream)

    columns = []

    row_index = 0
    while run:

        if len(columns) == 0:
            dataset = pd.read_csv(DATASET_PATH, nrows=5, skiprows=row_index)
            columns = list(dataset.columns.values)
        else:
            dataset = pd.read_csv(DATASET_PATH, nrows=5, skiprows=row_index, names=columns)

        dataset = dataset.rename(columns={'TIMESTAMP': 'time'})
        
        if len(dataset.index) == 0:
            print("End of dataset")
            break

        row_index += 5

        print("Writing 5 rows")

        quix_functions.data_handler(dataset)

        time.sleep(1)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target=get_data)
    thread.start()

    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
    pass
