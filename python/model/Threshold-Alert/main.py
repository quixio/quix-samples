from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader
from quixstreaming.app import App
from threshold_function import threshold
import os

# Create a client. The client helps you to create input reader or output writer for specified topic.
client = QuixStreamingClient(
    'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9yb2xlcyI6IiIsImlzcyI6Imh0dHBzOi8vYXV0aC5kZXYucXVpeC5haS8iLCJzdWIiOiJhdXRoMHw2YjljOGI1YS1kNGY0LTQzMDUtOTdlYS1hYzQ2ZmI2OGUzODUiLCJhdWQiOlsiaHR0cHM6Ly9wb3J0YWwtYXBpLmRldi5xdWl4LmFpLyIsImh0dHBzOi8vcXVpeC1kZXYuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY0MTgwODE4MywiZXhwIjoxNjQ0NDAwMTgzLCJhenAiOiI2MDRBOXE1Vm9jWW92b05Qb01panVlVVpjRUhJY2xNcyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.ISUihdFG2rVCBXG_wjEbJ2fTYXwECX_QiN29IFITWTLvfjUSDHZeNCHdyN78oL4leGxTAUbVN7NPVlP_edV68Z-VGR6AhvDpXHZ8YQZkoSUMngcac0wTW2VHBIsBAyTCxD2ucQrt73m_P1rP_apQYkhpaPzA5RIK90anNvRLh59kIYlDYkrox6gyP_OA3pntnCTDdvmtGfHdt3z1dWz4EkbqjlMjVVNadxd2t1-mtQTPV1VbMZd-0CIUDb56HasOV9jaEBwpP894pKvHej6qGGrzuVBc7Kb4s2-2DXMNulifEUQOIJsgvJLkFBn_PsyDLFZmHRPA5yIDbulK-ZoivQ')
# temporary (needed for dev)
client.api_url = "https://portal-api.dev.quix.ai"

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

# Environment variables
input_topic = client.open_input_topic('{placeholder:input}', "default-consumer-group")
output_topic = client.open_output_topic('{placeholder:output}')
threshold_value = float('{placeholder:ParameterName}')
parameter_name = str('{placeholder:ThresholdValue}')


# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):
    # Create a new stream to output data
    output_stream = output_topic.create_stream(input_stream.stream_id + "-threshold-alert")
    output_stream.properties.parents.append(input_stream.stream_id)

    print(type(output_stream))

    # handle the data in a function to simplify the example
    quix_function = threshold(input_stream, output_stream, parameter_name, threshold_value)

    # React to new data received from input topic.
    input_stream.events.on_read += quix_function.on_event_data_handler
    input_stream.parameters.on_read += quix_function.on_parameter_data_handler

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

