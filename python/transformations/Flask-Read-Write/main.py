from flask import Flask
import os
import requests
import json
import time
from datetime import datetime
import urllib.parse

auth_token = '{placeholder:token}'

telemetry_query_base_url = 'https://telemetry-query-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/'
streaming_writer_base_url = 'https://writer-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/'

app = Flask("Hello Flask I/O")


# a helper method to do our HTTP posts
def post(url, payload):
    headers = {'Authorization': 'Bearer ' + auth_token, 'Content-type': 'application/json'}
    payload = json.dumps(payload)
    r = requests.post(url, data=payload, headers=headers)
    return r


@app.route("/")
def hello_world():
    return "<p><a href='/streams'>Read Streams</a></p>"


@app.route("/write/<stream_id>")
def write_event(stream_id):
    # get the input topic
    topic = os.environ["topic"]

    # create the payload to send to the stream
    # create your own events, this is just an example
    payload = [{
            "timestamp": time.time_ns(),
            "id": "MyEventId",
            "value": "MyEventValue at {}".format(datetime.now()),
            "tags": {
                "tag1": "1",
                "tag2": "2",
                "tag3": "3"
            }}]

    # generate the URL to use
    url = "{}topics/{}/streams/{}/events/data".format(streaming_writer_base_url, topic, stream_id)

    # post the payload to the URL
    result = post(url, payload)
    print(result.status_code)

    # create a heading for the page and the data
    response = "<p><a href='/'>HOME</a> | <a href='/streams'>Streams</a></p><br/><br/>"

    # display the HTTP status code
    response = response + "{} - {}".format(result.status_code, result.reason)
    return response


@app.route("/streams")
def get_streams():
    # build the URL
    url = telemetry_query_base_url + "streams"

    # create the payload, just need topic and the topic name
    payload = {"topic": "{}".format(os.environ["topic"])}

    # post the payload to the URL
    result = post(url, payload)

    # load the json
    streams = json.loads(result.text)

    # build the html response
    response = "<p><a href='/'>HOME</a></p>"
    response = response + "These are the streams for the topic <b>{}</b><br/><br/>".format(os.environ["topic"])

    # display the list of returned streams
    for s in streams:
        safe_string = urllib.parse.quote_plus(s["streamId"])
        response = "{}<a href='/write/{}'>{}</a><br/>".format(response, safe_string, s["streamId"])

    # add some helpful advice
    response = response + "<br/>Click a stream to send an event to it" \
                          "<br/>If you don't see any streams either ensure data is " \
                          "arriving into the topic or turn on topic persistence"

    return response


app.run(debug=True, host="0.0.0.0", port=80)



