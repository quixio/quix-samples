import quixstreams as qx
from quix_functions import QuixFunctions
import traceback
from threading import Thread
import os
import websocket
import rel
import json

web_socket = None

try:

    # Which currency pairs are you interested in?
    asset_id_base = os.environ["asset_id_base"]
    asset_id_quote = os.environ["asset_id_quote"]

    # COIN API Key
    coin_api_key = os.environ["coin_api_key"]

    if coin_api_key == '':
        raise ValueError('Please update coin_api_key env var with your COIN API Key')

    # Quix injects credentials automatically to the client.
    # Alternatively, you can always pass an SDK token manually as an argument.
    client = qx.QuixStreamingClient()

    # Open the output topic where to write data out
    print("Opening output topic")
    producer_topic = client.get_topic_producer(os.environ["output"])

    stream_producer = producer_topic.create_stream("{}-{}-quotes".format(asset_id_base, asset_id_quote))

    # Give the stream human-readable name. This name will appear in data catalogue.
    stream_producer.properties.name = "{}/{} Exchange Rate".format(asset_id_base, asset_id_quote)

    # Save stream in specific folder in data catalogue to help organize your workspace.
    stream_producer.properties.location = "/Coin API/{}-{}".format(asset_id_base, asset_id_quote)


    def on_message(ws, message):
        quix_functions = QuixFunctions(stream_producer)
        ms = json.loads(message)
        quix_functions.data_handler(ms['asset_id_base'], ms['asset_id_quote'], ms['time'], ms['rate'])


    def on_error(ws, error):
        print("Websocket error: " + error)


    def on_close(ws, close_status_code, close_msg):
        print("Websocket connection closed")


    def on_open(ws):
        print("CONNECTED!")  # message to the Quix UI to let it know a connection has been made

        print("Subscribing to {}/{} rates".format(asset_id_base, asset_id_quote))

        ws.send(json.dumps(
            {'type': 'hello', 'apikey': coin_api_key, 'heartbeat': False, 'subscribe_data_type': ["exrate"],
             "subscribe_filter_asset_id": [f"{asset_id_base}/{asset_id_quote}"]}))


    def before_shutdown():
        global web_socket

        print("Closing websocket")
        web_socket.close()

        print("Aborting event listener")
        rel.abort()


    if __name__ == "__main__":
        web_socket = websocket.WebSocketApp("ws://ws-sandbox.coinapi.io/v1",
                                            on_open = on_open,
                                            on_message = on_message,
                                            on_error = on_error,
                                            on_close = on_close)

        # Set dispatcher to automatic reconnection, 5-second reconnect delay if connection closed unexpectedly
        web_socket.run_forever(dispatcher = rel, reconnect = 5)

        # run the dispatcher in a thread
        thread = Thread(target = rel.dispatch)

        # start the dispatcher thread
        thread.start()

        # run the Quix App, creating topics and listening for events as needed
        # before shutdown call before_shutdown
        qx.App.run(before_shutdown = before_shutdown)

        print("Shutting down")

except Exception:
    print("ERROR: {}".format(traceback.format_exc()))
