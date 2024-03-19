import os
from quixstreams import Application
from dotenv import load_dotenv

load_dotenv()

app = Application.Quix("transformation-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

sdf = sdf.update(lambda row: logger.debug(row))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    try:
        app.run(sdf)
    except Exception as e:
        print(f"An error occurred while running the application. {e}")