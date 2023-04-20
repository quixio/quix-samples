import quixstreams as qx
import os
import json
import requests
import time
from threading import Thread

# should the main loop run?
run = True

client = qx.QuixStreamingClient()
api_key = os.environ["api_key"]

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

producer_topic = client.get_topic_producer(os.environ["output"])

def get_data():
    while run:
        start = time.time()
        print("Loading new data.")
        cameras = requests.get(
            "https://api.tfl.gov.uk/Place/Type/JamCam/?app_id=QuixFeed&app_key={}".format(api_key))

        cameras_list = cameras.json()

        for camera in cameras_list:
            camera_id = camera["id"]

            producer_topic.get_or_create_stream(camera_id).events.add_timestamp_nanoseconds(time.time_ns()) \
                .add_value("camera", json.dumps(camera)) \
                .publish()    

            print("Sent camera " + camera_id)

        sleep_time = 120 - (time.time() - start)

        if sleep_time > 0:
            print("Sleep for " + str(sleep_time))
            time.sleep(sleep_time)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    # handle termination signals and close streams
    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()