from quixstreaming import QuixStreamingClient
from quixstreaming.state.localfilestorage import LocalFileStorage
import quixstreaming as qs

# use feed parser
import feedparser

import os
from datetime import datetime
import json
import time
import threading


storage = LocalFileStorage()
client = QuixStreamingClient()

output_topic = client.open_output_topic(os.environ["output"])
stream_writer = output_topic.create_stream("RSS Data" + datetime.now().strftime("%m-%d-%Y--%H-%M-%S"))

# should the main loop keep going?
shutting_down = False

# store the id's so we dont duplicate feed items
ids = []


def log(message: str):
    print("{} - {}".format(datetime.now(), message))

if storage.containsKey("rss_ids"):
    ids = storage.get("rss_ids")
    log("ids loaded from state")

def main():

    while not shutting_down:
        
        rss = feedparser.parse(os.environ["rss_url"])
        new_items=0
        
        # iterate through the entries
        for e in rss.entries: 
            rss_id = e["id"]

            if rss_id in ids:
                log("Already seen this one!")
                continue # comment this line if you want constant data and dont care about duplicates

            # add the id, so we know we've seen this one
            ids.append(rss_id)
            
            # write the rss feed entry to Quix as an event
            stream_writer.events \
                .add_timestamp(datetime.now()) \
                .add_value("RSS_RAW", json.dumps(e))\
                .write()

            # also write it as parameter data
            # these will be individual parameters, groupable by RSS_ID
            
            timestamp = stream_writer.parameters.buffer.add_timestamp(datetime.now())
            
			# iterate the datas keys 
            for key in e.keys():
                value = str(e[key]) # convert everything to a string
                timestamp \
                    .add_tag("RSS_ID", rss_id) \
                    .add_value(key, value)

            # write the data
            timestamp.write()

            # just flush to be sure its all gone
            stream_writer.events.flush()
            stream_writer.parameters.flush()
            
            new_items += 1
        
        log("Written {} RSS items to stream".format(new_items))

        # this is optional but saves a bit of resource if nothing is happening
        # sleep for a bit, nothing new is happening.
        # stop sleeping if process termination requested
        # dont sleep if there was something new, there might be some hot news breaking
        sleep_time = 50 # can change the sleep time to whatever you want
        sleeping = sleep_time if new_items > 0 else 0
        message = "Not much is happening" if new_items == 0 else "Things are heating up"
        log("{} sleeping for {} seconds".format(message, abs(sleeping - sleep_time)))

        #sleeping = 0
        while sleeping <= 5 and not shutting_down:
            sleeping = sleeping + 1
            time.sleep(1)


# handle shutdown nicely
def before_shutdown():
    global shutting_down
    # tell the main loop were heading out
    shutting_down = True
	
    # commit the latest rss_id list to the persisted storage
    storage.set("rss_ids", ids)
	
if __name__ == "__main__":
    # create and start the thread where all the good stuff happens
    main_thread = threading.Thread(target = main)
    main_thread.start()

    # run the app and handle shutdown nicely
    qs.App.run(before_shutdown=before_shutdown)

    main_thread.join()