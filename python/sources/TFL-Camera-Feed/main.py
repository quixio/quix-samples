import time
import os
import json
import requests
from quixstreaming import QuixStreamingClient


client = QuixStreamingClient()
frame_rate = int(os.environ["frame_rate"])
api_key = os.environ["api_key"]

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

output_topic = client.open_output_topic(os.environ["output"])

while True:
    start = time.time()
    print("Loading new data.")
    cameras = requests.get(
        "https://api.tfl.gov.uk/Place/Type/JamCam/?app_id=QuixFeed&app_key={}".format(api_key))

    cameras_list = cameras.json()

    for camera in cameras_list:
        camera_id = camera["id"]

        output_topic.get_or_create_stream(camera_id).events.add_timestamp_nanoseconds(time.time_ns()) \
            .add_value("camera", json.dumps(camera)) \
            .write()    

        print("Sent camera " + camera_id)

    sleep_time = 120 - (time.time() - start)

    if sleep_time > 0:
        print("Sleep for " + str(sleep_time))
        time.sleep(sleep_time)





