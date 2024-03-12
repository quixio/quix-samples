from quixstreams import Application
import os
import requests


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
app = Application.Quix(consumer_group="slack-notifications")

print("Opening input and output topics")
input_topic = app.topic(os.getenv("input", ""))

webhook_url = os.getenv("webhook_url", "")

if input_topic is None:
    raise ValueError("input topic is required")

if webhook_url is None:
    raise ValueError("webhook url is required")

# create the streaming dataframe
sdf = app.dataframe(input_topic)

# filter out inbound data without the 'message' column
sdf = sdf[sdf.contains("message")]

# this code assumes the data contains a 'messages' column
# which contains the message to be sent to slack
def send_to_slack(data):
    # transmit your message to slack immediately
    # use a rolling window and state to batch sending
    # https://quix.io/docs/quix-streams/windowing.html
    slack_message = {"text": str(data["message"])}
    requests.post(webhook_url, json = slack_message)

# apply a function to the incoming data
sdf = sdf.apply(send_to_slack)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)
