from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.app import App
from quix_function import QuixFunction
import os

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

# Open input and output topic connections.
input_topic_bikes = client.open_input_topic(os.environ["bike-input"])
input_topic_weather = client.open_input_topic(os.environ["weather-input"])
output_topic = client.open_output_topic(os.environ["output"])

# Create the streams: collections of data that belong to a single session of a single source.
bike_stream_writer = output_topic.create_stream("NY-Real-Time-Bikes-NY-Timestamp")
bike_stream_writer.properties.name = "Number of available bikes in NY with local NY timestamp"
bike_stream_writer.properties.location = "/ML_Predictions"

prediction_1h_stream_writer = output_topic.create_stream("PRED_ML_1h")
prediction_1h_stream_writer.properties.name = "Prediction ML Model 1-hour ahead forecast"
prediction_1h_stream_writer.properties.location = "/ML_Predictions"

prediction_1d_stream_writer = output_topic.create_stream("PRED_ML_1d")
prediction_1d_stream_writer.properties.name = "Prediction ML Model 1-day ahead forecast"
prediction_1d_stream_writer.properties.location = "/ML_Predictions"

quix_function = QuixFunction.__init__(bike_stream_writer, prediction_1h_stream_writer,
                                      prediction_1d_stream_writer)


# define callback for bike streams
def read_bike_stream(new_stream: StreamReader):
    print("New bike stream read:" + new_stream.stream_id)
    new_stream.parameters.on_read_pandas += quix_function.on_bike_parameter_data_handler


# define callback for weather streams
def read_weather_stream(new_stream: StreamReader):
    buffer_options = ParametersBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100
    buffer_options.buffer_timeout = 100
    buffer = new_stream.parameters.create_buffer(buffer_options)

    print("New weather stream read:" + new_stream.stream_id)

    buffer.on_read_pandas += quix_function.on_weather_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic_bikes.on_stream_received += read_bike_stream
input_topic_weather.on_stream_received += read_weather_stream

input_topic_bikes.start_reading()  # initiate read for bike data
input_topic_weather.start_reading()  # initiate read for weather data

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()

print("Exiting")
