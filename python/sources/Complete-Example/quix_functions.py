import quixstreams as qx
import datetime


class QuixFunction:
    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    # An example of how to set the various stream properties
    def set_stream_properties(self):
        print("---- Setting stream properties ----")
        self.stream_producer.properties.name = "Python Sample 99"
        self.stream_producer.properties.location = "/test/location"
        self.stream_producer.properties.metadata["meta"] = "is"
        self.stream_producer.properties.metadata["working"] = "well"
        self.stream_producer.properties.parents.append("testParentId1")
        self.stream_producer.properties.parents.append("testParentId2")
        self.stream_producer.properties.time_of_recording = datetime.datetime.utcnow()

    # An example of how to set the various parameter definitions
    # Defining your parameters is an optional but useful step
    def send_parameter_definitions(self):
        print("---- Sending parameter definitions ----")
        self.stream_producer.timeseries \
            .add_definition("param_at_root", "Root Parameter",
                            "This is a root parameter as there is no default location")
        self.stream_producer.timeseries.default_location = "/Base/"
        self.stream_producer.timeseries.add_definition("string_param",
                                                     "String parameter",
                                                     "This is a string parameter description") \
            .add_definition("parameter2", description="This is parameter 2") \
            .set_unit("%") \
            .set_format("{0}%") \
            .set_range(
            0, 100)
        self.stream_producer.timeseries.add_location("/NotBase") \
            .add_definition("num_param") \
            .set_unit("kph") \
            .set_range(0, 300) \
            .set_custom_properties("{test}")

    # Send parameter data with a defined epoch
    def send_parameter_data_epoch(self):
        print("---- Sending parameter data ----")

        # Set the epoch
        self.stream_producer.timeseries.buffer.epoch = datetime.datetime(2018, 1, 1)

        self.stream_producer.timeseries.buffer_size = 500
        self.stream_producer.timeseries.buffer_size_in_nanoseconds = 5e+9  # 5000 ms
        self.stream_producer.timeseries.buffer_timeout = 400
        self.stream_producer.timeseries.default_location = "/default"
        self.stream_producer.timeseries.buffer.default_tags["Tag1"] = "tag one"
        self.stream_producer.timeseries.buffer.default_tags["Tag2"] = "tag two"
        # nanoseconds since start of epoch
        self.stream_producer.timeseries.buffer \
            .add_timestamp_nanoseconds(54323000000) \
            .add_value("string_param", "value1") \
            .add_value("num_param", 83.756) \
            .publish()  # 2018-01-01 15:05:23 GMT as nanoseconds since unix epoch

    # Set timestamp for parameters explicitly
    def send_parameter_data_specific_date_time(self):
        self.stream_producer.timeseries.buffer \
            .add_timestamp(datetime.datetime(2018, 1, 1, 11, 42, 39, 321)) \
            .add_value("string_param", "value1") \
            .add_value("num_param", 123.43) \
            .add_tag("Tag2", "tag two updated") \
            .add_tag("Tag3", "tag three") \
            .publish()  # When using a datetime, previously configured epoch is ignored

    # Sent an epoch then use seconds and ms time delta
    def send_parameter_time_delta(self):
        self.stream_producer.timeseries.buffer.epoch = datetime.datetime(2018, 1, 2)
        self.stream_producer.timeseries.buffer \
            .add_timestamp(datetime.timedelta(seconds=1, milliseconds=555)) \
            .add_value("num_param", 123.32) \
            .publish()  # 1 second 555 milliseconds after 2018-01-02

    def send_event_definitions(self):
        self.stream_producer.events.add_definition("event_at_root", "Root Event",
                                          "This is a root event as there is no default location")
        self.stream_producer.events.default_location = "/Base"
        self.stream_producer.events.add_definition("event_1", "Event One", "This is test event number one") \
            .add_definition("event_2", description = "This is event 2").set_level(qx.EventLevel.Debug).set_custom_properties(
            "{test prop for event}")
        self.stream_producer.events.add_location("/NotBase").add_definition("event_3").set_level(qx.EventLevel.Critical)

    def send_event_data(self):
        self.stream_producer.events.default_location = "/default"
        self.stream_producer.events.default_tags["Tag1"] = "tag one"
        self.stream_producer.events.default_tags["Tag2"] = "tag two"
        self.stream_producer.events.epoch = datetime.datetime(2018, 1, 1)
        self.stream_producer.events \
            .add_timestamp(datetime.datetime(2018, 1, 1, 11, 31, 22, 111)) \
            .add_value("event_1", "event value 1") \
            .add_tag("Tag2", "tag two updated") \
            .add_tag("Tag3", "tag three") \
            .publish()  # When using a datetime, previously configured epoch is ignored
        self.stream_producer.events \
            .add_timestamp_nanoseconds(57383000000) \
            .add_value("event_1", "event value 1.1") \
            .add_value("event_2", "event value 2") \
            .publish()  # 2018-01-01 15:56:23 GMT as nanoseconds since unix epoch
        self.stream_producer.events.epoch = datetime.datetime(2018, 1, 2)
        self.stream_producer.events \
            .add_timestamp(datetime.timedelta(seconds=1, milliseconds=555)) \
            .add_value("event_3", "3232") \
            .publish()  # 1 second 555 milliseconds after 2018-01-02

    # Close the stream when needed
    def close_stream(self):
        print("Closing")
        self.stream_producer.close(qx.StreamEndType.Aborted)

    # Handle exceptions
    def on_write_exception_handler(self, stream_producer: qx.StreamProducer, ex: BaseException):
        print(ex.args[0])