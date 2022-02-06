from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from quix_functions import QuixFunctions
import requests
import time
import traceback
from threading import Thread
import os

# should the main loop run?
run = True

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as a parameter.
client = QuixStreamingClient('{placeholder:sdktoken}')

# Open the output topic where to write data out
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# Which currency pairs are you interested in?
from_currency = "{}".format(os.environ["from_currency"])  # e.g."BTC"
to_currency = "{}".format(os.environ["to_currency"])  # e.g."USD,GBP"

url = 'https://rest.coinapi.io/v1/exchangerate/{0}?filter_asset_id={1}'.format(from_currency, to_currency)

# COIN API Key
coin_api_key = "{}".format(os.environ["coin_api_key"])

if coin_api_key == '':
    raise ValueError('Please update coin_api_key env var with your COIN API Key')

headers = {'X-CoinAPI-Key': coin_api_key}

output_stream = output_topic.create_stream("coin-api")

# Give the stream human readable name. This name will appear in data catalogue.
output_stream.properties.name = "Coin API"

# Save stream in specific folder in data catalogue to help organize your workspace.
output_stream.properties.location = "/Coin API"


def get_data():
    global run

    quix_functions = QuixFunctions(output_stream)

    while run:
        try:
            response = requests.get(url, headers=headers)

            data = response.json()

            rows = data['rates']

            quix_functions.data_handler(rows, from_currency)

            # We sleep for 15 minutes so we don't reach free COIN API account limit.
            # Stop sleeping if process termination requested
            sleeping = 0
            while sleeping <= 900 and run:
                sleeping = sleeping + 1
                time.sleep(1)

        except Exception:
            print(traceback.format_exc())


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target=get_data)
    thread.start()

    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
