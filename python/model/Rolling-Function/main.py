from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader
from quixstreaming.app import App
from rolling_function import RollingFunction
import os
import pandas as pd


# Create a client. The client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9yb2xlcyI6IiIsImlzcyI6Imh0dHBzOi8vYXV0aC5kZXYucXVpeC5haS8iLCJzdWIiOiJhdXRoMHw2YjljOGI1YS1kNGY0LTQzMDUtOTdlYS1hYzQ2ZmI2OGUzODUiLCJhdWQiOlsiaHR0cHM6Ly9wb3J0YWwtYXBpLmRldi5xdWl4LmFpLyIsImh0dHBzOi8vcXVpeC1kZXYuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY0MTgxODU2NCwiZXhwIjoxNjQ0NDEwNTY0LCJhenAiOiI2MDRBOXE1Vm9jWW92b05Qb01panVlVVpjRUhJY2xNcyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.TyBjtgyDJj2J16u2d7-xSSo8nfKb5yfQQtYdEQrjUdW5iwuyMHeNWWwvFGsMeTRjHot2XSMDHK6e5qXr5wUYHKxmcV4SdATfxDVBVGXAQJuAjgGMbIlx4zHiCXkyghKRk7QNVSn6Ee6pgiPH5NOSXSjaXLL-uLXkrzd0CSs6CuEv4cC2713jcumltPN2qAyk3nf5HN33y3FholJ8KMVlTGedstcy_E6hgWFZzkIG_FsDVB_ulGU8LM6OnY9oyFzhwBCrftZ17EZykHcUVO3Q1uNiX6XR1dRdKZDJwKsCy809K2-Ghz-MFpgsrHSDSRZQu6JtpeIdNVM_u2bsiB9n5Q')
# temporary (needed for dev)
client.api_url = "https://portal-api.dev.quix.ai"

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

# Define environmental variables
input_topic = client.open_input_topic(os.environ["Quix__Workspace__Id"]+"-"+os.environ["input"], "default-consumer-group")
output_topic = client.open_output_topic(os.environ["Quix__Workspace__Id"]+"-"+os.environ["output"])
parameter_name = str(os.environ["parameter_name"])

# Define window out of window_type and window_value environmental variables
if os.environ["window_type"] == 'Number of Observations':
    window = int(os.environ["window_value"])
elif os.environ["window_type"] == 'Time Period':
    window = pd.Timedelta(str(os.environ["window_value"]))
else:
    window = None

# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):

    # Create a new stream to output data
    output_stream = output_topic.create_stream(input_stream.stream_id + "-moving-average")
    output_stream.properties.parents.append(input_stream.stream_id)

    # handle the data in a function to simplify the example
    quix_function = RollingFunction(input_stream, output_stream, parameter_name, window)
        
    # React to new data received from input topic.
    input_stream.events.on_read += quix_function.on_event_data_handler
    input_stream.parameters.on_read_pandas += quix_function.on_parameter_data_handler

    # When input stream closes, we close output stream as well. 
    def on_stream_close(endType: StreamEndType):
        output_stream.close()
        print("Stream closed:" + output_stream.stream_id)

    input_stream.on_stream_closed += on_stream_close

# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()