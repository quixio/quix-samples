import quixstreams as qx

# use feed parser
import feedparser

import os
from datetime import datetime
import json
import time
import threading

storage = qx.LocalFileStorage()
client = qx.QuixStreamingClient()

producer_topic = client.get_topic_producer(os.environ["output"])
stream_producer = producer_topic.get_or_create_stream("RSS Data" + datetime.now().strftime("%m-%d-%Y--%H-%M-%S"))

# should the main loop keep going?
shutting_down = False

# store the hashes so we don't duplicate feed items
hashes = []


def log(message: str):
    print("{} - {}".format(datetime.now(), message))


if storage.contains_key("rss_hashes"):
    hashes = storage.get("rss_hashes")
    log("Hashes loaded from state")


def main():
    while not shutting_down:

        rss = feedparser.parse(os.environ["rss_url"])
        new_items = 0

        # iterate through the entries
        for e in rss.entries:
            e_hash = hash(e)

            if e_hash in hashes:
                log("Already seen this one!")
                continue  # comment this line if you want constant data and don't care about duplicates

            # add the hash, so we know we've seen this one
            hashes.append(e_hash)

            # write the rss feed entry to Quix as an event
            stream_producer.events \
                .add_timestamp(datetime.now()) \
                .add_value("RSS_RAW", json.dumps(e)) \
                .publish()

            # also write it as parameter data
            # these will be individual parameters, groupable by RSS_HASH

            timestamp = stream_producer.timeseries.buffer.add_timestamp(datetime.now())

            # iterate the datas keys
            for key in e.keys():
                value = str(e[key])  # convert everything to a string
                timestamp \
                    .add_tag("RSS_HASH", str(e_hash)) \
                    .add_value(key, value)

            # write the data
            timestamp.publish()

            # just flush to be sure it's all gone
            stream_producer.events.flush()
            stream_producer.timeseries.flush()

            new_items += 1

        log("Written {} RSS items to stream".format(new_items))

        # this is optional but saves a bit of resource if nothing is happening
        # sleep for a bit, nothing new is happening.
        # stop sleeping if process termination requested
        # don't sleep if there was something new, there might be some hot news breaking
        sleep_time = 50  # can change the sleep time to whatever you want
        sleeping = sleep_time if new_items > 0 else 0
        message = "Not much is happening" if new_items == 0 else "Things are heating up"
        log("{} sleeping for {} seconds".format(message, abs(sleeping - sleep_time)))

        # sleeping = 0
        while sleeping <= 5 and not shutting_down:
            sleeping = sleeping + 1
            time.sleep(1)


# handle shutdown nicely
def before_shutdown():
    global shutting_down
    # tell the main loop were heading out
    shutting_down = True

    # commit the latest rss_hashes list to the persisted storage
    storage.set("rss_hashes", hashes)


if __name__ == "__main__":
    # create and start the thread where all the good stuff happens
    main_thread = threading.Thread(target=main)
    main_thread.start()

    # run the app and handle shutdown nicely
    qx.App.run(before_shutdown=before_shutdown)

    main_thread.join()
