from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader, ParameterData, \
    ParameterValue, EventData
from quixstreaming.app import App
from prometheus_client import start_http_server, Summary, Counter, Gauge
from prometheus_client import Enum
import os


client = QuixStreamingClient()

print("Opening input and output topics")
input_topic = client.open_input_topic(os.environ["input"], "prometheus-sink")

# Create summaries
parameter_data_handler_processing_time = Summary('param_data_handler_seconds', 'Time spent processing parameter data')
event_data_handler_processing_time = Summary('event_data_handler_seconds', 'Time spent processing event data')
get_value_processing_time = Summary('get_value_seconds', 'get_value function processing time')
get_or_set_status_value_processing_time = Summary('get_or_set_status_value_seconds',
                                                  'get_or_set_status_value function processing time')
create_or_update_gauge_processing_time = Summary('create_or_update_gauge_seconds',
                                                 'create_or_update_gauge function processing time')

# setup the enum for service status
e = Enum('service_state', 'Status of the service', states=['starting', 'running'])

# setup counters and static gauges
parameter_value_counter = Counter("total_parameter_values", "Total parameter values handled")
event_value_counter = Counter("total_event_values", "Total event values handled")
unique_tag_key_counter = Counter("total_unique_tag_keys", "Total unique tag keys")
unique_tag_value_counter = Counter("total_unique_tag_values", "Total unique tag values")
streams_handled_gauge = Gauge("streams", "Total streams handled")
streams_open_gauge = Gauge("streams_open", "Total open streams")

# storage for data statistics (min/max values)
data_stats = {}
# storage for dynamically created gauges
gauges = {}
# storage for tags seen
tags = []

# get the string, numeric or binary value from the parameter value
@get_value_processing_time.time()
def get_value(parameter: ParameterValue):
    if parameter.string_value is not None:
        return {"type": "string", "value": parameter.string_value}
    if parameter.numeric_value is not None:
        return {"type": "numeric", "value": parameter.numeric_value}
    if parameter.binary_value is not None:
        return {"type": "binary", "value": parameter.binary_value}

@get_or_set_status_value_processing_time.time()
def update_stats_and_metrics(parameter_name, value, suffix):

    # update the data stats
    data_stats[parameter_name + suffix] = value
    # update the metric
    create_or_update_gauge(parameter_name, value, suffix)

@create_or_update_gauge_processing_time.time()
def create_or_update_gauge(name, value: int, suffix):
    # build the unique key for this item
    dictionary_name = name + suffix + "_gauge"

    # if this item exists in the dictionary
    if dictionary_name in gauges:
        # update its value
        g = gauges[dictionary_name]
        g.set(value)
    else:
        # otherwise, create and set value
        g = Gauge(name + suffix, name + " " + suffix + " value")
        g.set(value)
        gauges[dictionary_name] = g

# determine if a value is unique
def value_is_unique(tag):
    if tag in tags:
        return False
    else:
        tags.append(tag)
        return True

@parameter_data_handler_processing_time.time()
def on_param_data_handler(data: ParameterData):

    # iterate the timestamps
    for t in data.timestamps:
        # iterate the parameters
        for parameter_name, p in t.parameters.items():

            # increment the total values handled counter
            parameter_value_counter.inc()

            # get the value type and value
            # these will be used below
            value_type = get_value(t.parameters[parameter_name])
            value = value_type["value"]

            # if value type is numeric
            if value_type["type"] == "numeric":
                # call the helper to update stats and metrics where appropriate
                update_stats_and_metrics(parameter_name, value, "")
                
            if value_type["type"] == "string":
                update_stats_and_metrics(parameter_name, len(value), "_length")
                
            if value_type["type"] == "binary":
                update_stats_and_metrics(parameter_name, len(value), "_length")
                

@event_data_handler_processing_time.time()
def on_event_data_handler(data: EventData):
    # increment the total values handled counter
    event_value_counter.inc()

    # iterate the tags
    for tag in data.tags.items():
        # get the key and value for convenience later
        tag_key = "key_" + tag[0]
        tag_value = "value_" + tag[1]

        # check tag is unique
        if value_is_unique(tag_key):
            # increment the total values handled counter
            unique_tag_key_counter.inc()

        # check value is unique
        if value_is_unique(tag_value):
            # increment the total values handled counter
            unique_tag_value_counter.inc()


def read_stream(input_stream: StreamReader):

    buffer = input_stream.parameters.create_buffer()
    # handle parameter data being received
    buffer.on_read += on_param_data_handler
    # handle event data being received
    input_stream.events.on_read += on_event_data_handler

    # count the total handled streams
    streams_handled_gauge.inc()
    # and the numer of open streams
    streams_open_gauge.inc()

    def on_stream_properties_changed():
        # if stream properties change. update the metrics
        create_or_update_gauge("stream_properties_parents", len(input_stream.properties.parents), "count")
        create_or_update_gauge("stream_properties_metadata", len(input_stream.properties.metadata), "count")

    def on_stream_close(endType: StreamEndType):
        # decrement when a stream is closed
        print("stream closed")
        streams_open_gauge.dec()

    # hook up the stream closed and properties changed event handlers
    input_stream.on_stream_closed += on_stream_close
    input_stream.properties.on_changed += on_stream_properties_changed

def shutdown():
    # do shut down tasks here
    pass

if __name__ == '__main__':
    print("Starting Prometheus server")

    # Start up the prometheus server to expose the metrics.
    # Use port 80, this is the only available port right now
    # NOTE: externally use an https url / port 433
    start_http_server(80)

    # set the state
    e.state('starting')

    # hook up the stream received event handler
    input_topic.on_stream_received += read_stream

    # set the state
    e.state('running')

    # call Quix SDK's App.run. This will create topics and keep the app running as long as required
    # when a termination signal is detected the app will stop and call the shutdown function
    App.run(before_shutdown=shutdown)
