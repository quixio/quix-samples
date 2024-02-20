from quixstreams import Application

import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("./.env", 'a+') as file: pass  # make sure the .env file exists
load_dotenv("./.env")


def sink(message):
    value = message['mykey']
    # write_to_db(value) # implement your logic to write data or send alerts etc

app = Application.Quix("destination-v1", auto_offset_reset = "latest")

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)

sdf = sdf.update(sink)

sdf = sdf.update(lambda row: print(row))

if __name__ == "__main__":
    app.run(sdf)