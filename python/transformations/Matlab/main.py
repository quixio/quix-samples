import quixstreams as qx
import os, math
import matlab.engine

print("INFO: starting MATLAB engine")
matlab_engine = matlab.engine.start_matlab()
print("INFO: started MATLAB engine")

client = qx.QuixStreamingClient()
input_topic = client.get_topic_consumer(os.environ["input"])
output_topic = client.get_topic_producer(os.environ["output"])

def on_data_received_handler(input_stream: qx.StreamConsumer, data: qx.TimeseriesData):
    with data:
        for ts in data.timestamps:    
            x = ts.parameters["x"].numeric_value
            y = ts.parameters["y"].numeric_value
            v = matlab.double([[x], [y]])
            M = matlab_engine.rot(v, math.pi / 180 * 45)
            ts.add_value("x45", M[0][0])
            ts.add_value("y45", M[1][0])
            print("x45:{}, y45:{}".format(M[0][0], M[1][0]))
        output_stream = output_topic.get_or_create_stream(input_stream.stream_id)
        output_stream.timeseries.publish(data)

def on_stream_received_handler(stream: qx.StreamConsumer):
    print("New stream: {}".format(stream.stream_id))
    stream.timeseries.on_data_received = on_data_received_handler

input_topic.on_stream_received = on_stream_received_handler

print("Listening to streams. Press CTRL-C to exit.")
qx.App.run()