from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
from google.cloud import pubsub_v1
from google.auth import jwt
from google.api_core.exceptions import Cancelled as GoogleCancelledException
from concurrent.futures import TimeoutError
import json
from datetime import datetime
import os
import base64

subscriber = None
subscription = None
quix_stream = None


def connect_to_google():
    global subscriber
    global subscription

    if quix_stream is None:
        print("Not connected to Quix")
        return False

    project_id = os.environ["google_project_id"]
    subscription_id = os.environ["google_subscription_id"]
    service_account_info = json.load(open('../certificates/google_key.json'))
    audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

    credentials = jwt.Credentials.from_service_account_info(
        service_account_info, audience=audience
    )

    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

    quix_functions = QuixFunctions(quix_stream)

    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # when a message arrives from google, call the callback to handle the message
    subscription = subscriber.subscribe(subscription_path, callback=quix_functions.callback)
    print(f"Listening for messages on {subscription_path}..\n")

    print("CONNECTED!")

    with subscriber:
        try:
            subscription.result()
        except TimeoutError:
            close_google_subscription()
        except GoogleCancelledException:
            print("Expected GoogleCancelledException. Nothing to worry about here")


def connect_to_quix():
    global quix_stream

    quix_client = QuixStreamingClient()

    print("Opening output topic")
    output_topic = quix_client.open_output_topic(os.environ["output"])
    quix_stream = output_topic.create_stream()

    quix_stream.properties.location = "Raw Data"
    quix_stream.properties.name = "{} - {}".format("GooglePubSub", datetime.utcnow().strftime("%d-%m-%Y %X"))


def close_google_subscription():
    global subscriber
    global subscription

    if subscription is None: return

    subscriber.close()
    subscription.cancel()  # Trigger the shutdown.
    subscription.result()  # Block until the shutdown is complete.


def write_base64_to_file_as_binary(b64, file_name):
    # decode base64
    decoded = base64.b64decode(b64)
    # convert to byte array
    byte_array = bytearray(decoded)
    # write bytes to zip file
    f = open(file_name, "wb")
    f.write(byte_array)
    f.close()


def write_variable_to_file(variable, file_path):
    path = file_path
    dirname = os.path.dirname(path)

    # ensure dir exists
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    environment_variable_value = os.environ[variable]
    write_base64_to_file_as_binary(environment_variable_value, file_path)


def before_shutdown():
    print('Closing streams...')
    close_google_subscription()


print("Spooling fusion generators")

# generate the google_key.json file needed using the base 64 encoded value from environment variables.
write_variable_to_file("google_key", "../certificates/google_key.json")

# connect to Quix, open the output topic and create a stream
connect_to_quix()

# connect to google and start listening for data
connected = connect_to_google()

if connected is False:
    print('Exiting')
else:
    # Wait for termination signals and handle graceful shutdown
    App.run(before_shutdown=before_shutdown)
    print('Exiting')


