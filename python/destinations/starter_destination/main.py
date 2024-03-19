from quixstreams import Application
import os

from dotenv import load_dotenv
load_dotenv()

# you decide what happens here!
def sink(message):
    value = message['mykey']
    # write_to_db(value) # implement your logic to write data or send alerts etc

    # for more help using QuixStreams see the docs:
    # https://quix.io/docs/quix-streams/introduction.html

app = Application.Quix("destination-v1", auto_offset_reset = "latest")

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)

# call the sink function for every message received.
sdf = sdf.update(sink)

# you can print the data row if you want to see what's going on.
sdf = sdf.update(lambda row: print(row))

if __name__ == "__main__":
    app.run(sdf)