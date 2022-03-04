from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.app import App
from quix_function import QuixFunction
from flask import Flask
import threading
import os

streams = {}
app = Flask("Dashboard")


@app.route("/dashboard/<streamId>")
def get_board(streamId:str):
    
    board = streams[streamId]
    return board.dashboard[["TAG__LapNumber","EngineRPM"]].to_html(classes='data'), 200


def data_sub():

    # Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
    client = QuixStreamingClient()

    print("Opening input topic")
    input_topic = client.open_input_topic(os.environ["input"])


    # read streams
    def read_stream(input_stream: StreamReader):
        print("New stream read:" + input_stream.stream_id)

        # handle the data in a function to simplify the example
        quix_function = QuixFunction()
        streams[input_stream.stream_id] = quix_function
        input_stream.parameters.on_read += quix_function.on_parameter_data_handler


    # Hook up events before initiating read to avoid losing out on any data
    input_topic.on_stream_received += read_stream

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")
    
    # Handle graceful exit
    App.run()



t = threading.Thread(target=data_sub)
t.daemon = True
t.start()



app.run(debug=True, host="0.0.0.0", port=80)