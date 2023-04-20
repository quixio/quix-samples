import quixstreams as qx
from quix_function import QuixFunction
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open input and output topic connections.
consumer_topic_bikes = client.get_topic_consumer(os.environ["bike_input"])
consumer_topic_weather = client.get_topic_consumer(os.environ["weather_input"])
producer_topic = client.get_topic_producer(os.environ["output"])

# Create the streams: collections of data that belong to a single session of a single source.
bike_stream_producer = producer_topic.create_stream("NY-Real-Time-Bikes-NY-Timestamp")
bike_stream_producer.properties.name = "Number of available bikes in NY with local NY timestamp"
bike_stream_producer.properties.location = "/ML_Predictions"

prediction_1h_stream_producer = producer_topic.create_stream("PRED_ML_1h")
prediction_1h_stream_producer.properties.name = "Prediction ML Model 1-hour ahead forecast"
prediction_1h_stream_producer.properties.location = "/ML_Predictions"

prediction_1d_stream_producer = producer_topic.create_stream("PRED_ML_1d")
prediction_1d_stream_producer.properties.name = "Prediction ML Model 1-day ahead forecast"
prediction_1d_stream_producer.properties.location = "/ML_Predictions"

quix_function = QuixFunction(bike_stream_producer, prediction_1h_stream_producer,
                             prediction_1d_stream_producer)


# define callback for bike streams
def read_bike_stream(new_stream: qx.StreamConsumer):
    print("New bike stream read:" + new_stream.stream_id)
    new_stream.timeseries.on_dataframe_received = quix_function.on_bike_parameter_data_handler


# define callback for weather streams
def read_weather_stream(new_stream: qx.StreamConsumer):
    buffer_options = qx.TimeseriesBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100
    buffer_options.buffer_timeout = 100
    buffer = new_stream.timeseries.create_buffer(buffer_options)

    print("New weather stream read:" + new_stream.stream_id)

    buffer.on_dataframe_released = quix_function.on_weather_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
consumer_topic_bikes.on_stream_received = read_bike_stream
consumer_topic_weather.on_stream_received = read_weather_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
qx.App.run()

print("Exiting")
