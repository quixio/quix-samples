from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
import os
import pandas as pd 
import time
from threading import Thread

# should the main loop run?
run = True

DATASET_PATH = "./data/data.csv"

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])
output_stream = output_topic.create_stream('rawdata-in-stream')

output_stream.properties.name = 'raw_data'
output_stream.properties.location = '/dataset/raw_data'


def get_data():
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

        # Write Data to Stream
        output_stream.parameters.write(dataset)
        output_stream.parameters.flush()

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
