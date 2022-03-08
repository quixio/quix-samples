from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from twitter_function import TwitterFunction
import requests
import json
import time
from requests.exceptions import ChunkedEncodingError
import traceback
from threading import Thread
import os

# should the main loop run?
run = True

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic where to write data out
output_topic = client.open_output_topic(os.environ["output"])

# Twitter bearer token goes here
bearer_token = os.environ["twitter_bearer_token"]

if bearer_token is None:
    raise ValueError('You need to set the twitter_bearer_token to your Twitter developer bearer token')

# Twitter search parameters
twitter_search = os.environ["twitter_search_params"]


# define code to create the output stream
def create_stream():
    output_stream = output_topic.create_stream()
    output_stream.properties.name = "twitter_stream_results"
    output_stream.properties.location = "/twitter_data"

    return output_stream


# define the code to create the headers for the http connection
def create_headers(token):
    if token is None:
        raise Exception("Bearer token not set")

    headers = {"Authorization": "Bearer {}".format(token)}
    return headers


# define the code to get the existing rules from the twitter api
def get_rules(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print("Current Rules:" + json.dumps(response.json()))
    return response.json()


# code to delete the rules..
def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


# code to create the rules..
def set_rules(headers):
    sample_rules = [
        {"value": twitter_search, "tag": "my_search"}
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


# here were going to get the stream and handle its output
# we'll do this by streaming the results into Quix
def get_stream(headers, output_stream):
    global run

    TwitterFunction.__init__(output_stream)

    while run:
        try:
            with requests.get(
                    "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
            ) as response:
                print(response.status_code)
                if response.status_code != 200:
                    raise Exception(
                        "Cannot get stream (HTTP {}): {}".format(
                            response.status_code, response.text
                        )
                    )
                for response_line in response.iter_lines():

                    # exit the loop if kill signal received
                    if not run:
                        break

                    if response_line:
                        json_response = json.loads(response_line)

                        # get the data
                        data = json_response["data"]
                        # we will store the tag in quix too so get the rules used to obtain this data
                        matching_rules = json_response["matching_rules"]

                        TwitterFunction.data_handler(matching_rules, data)

        except ChunkedEncodingError:
            # if we get a ChunkedEncodingError error sleep then try again
            print(traceback.format_exc())
            time.sleep(6)
            continue

        except Exception:
            # some unexpected error occurred.. stop the loop
            print("Stopping loop because of un-handled error")
            print(traceback.format_exc())
            run = False


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    global output_topic

    headers = create_headers(bearer_token)
    rules = get_rules(headers)
    delete_all_rules(headers, rules)
    set_rules(headers)
    output_stream = create_stream()

    thread = Thread(target=get_stream, args=(headers, output_stream))
    thread.start()

    # wait for sigterm
    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
