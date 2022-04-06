from quixstreaming import StreamWriter, ParameterData
import json
from datetime import datetime


def json_load(json_data):
    try:
        return json.loads(json_data)
    except ValueError as err:
        print("{} was bad json".format(str(json_data)))
        return -1


class ConversionFunctions:
    def __init__(self, output_topic: StreamWriter):
        self.output_topic = output_topic

    @staticmethod
    def write_event_to_stream(stream, name, data_string):
        stream.events \
            .add_timestamp(datetime.utcnow()) \
            .add_value(name, data_string) \
            .write()

    @staticmethod
    def write_param_data(data, stream):
        json_data_object = json.loads(data)
        timestamps = json_data_object["Timestamps"]

        numerics = None
        strings = None
        binaries = None

        # if the json has values for numerics, strings or binaries
        # temporarily store them for easy access
        if "NumericValues" in json_data_object:
            numerics = json_data_object["NumericValues"]
        if "StringValues" in json_data_object:
            strings = json_data_object["StringValues"]
        if "BinaryValues" in json_data_object:
            binaries = json_data_object["BinaryValues"]

        # local function to add values to the parameter_data
        def add_values(data_object, timestamp_index, pd_for_ts):
            for key in data_object.keys():
                value = data_object[key][timestamp_index]
                pd_for_ts.add_value(key, value)

        for ts_index, ts in enumerate(timestamps):

            # create the parameter data object
            parameter_data = ParameterData()

            # add a timestamp
            pd_ts = parameter_data.add_timestamp_nanoseconds(ts)

            # if data exists for numerics, strings or binaries, add it
            if numerics:
                add_values(numerics, ts_index, pd_ts)
            if strings:
                add_values(strings, ts_index, pd_ts)
            if binaries:
                add_values(binaries, ts_index, pd_ts)

            # write the parameter_data to the stream
            stream.parameters.write(parameter_data)

    def raw_message_handler(self, msg):

        # decode the received byte array and load as json object
        raw_message = msg.value.decode("utf-8")
        json_object = json_load(raw_message)

        # if not valid json
        if not json_object:
            stream = self.output_topic.get_or_create_stream("unknown_payload")

            # just write the entire payload to an event
            stream.events \
                .add_timestamp(datetime.utcnow()) \
                .add_value("data", raw_message) \
                .write()

        # if valid json object
        if json_object:

            channel = json_object["channel"]

            stream = self.output_topic.get_or_create_stream(channel)

            # iterate the messages
            for m in json_object["messages"]:
                # get the data item
                data = m["data"]
                name = m["name"]
                print(name, data)

                # CloseStream is never json, so just write the event now
                if name == "CloseStream":
                    self.write_event_to_stream(stream, name, "Stream Closed")
                else:
                    # check for empty or just white space..
                    # if we have something then lets see if its good json
                    if data and data.strip():
                        # load as json
                        json_object = json_load(data)

                        # if it's not good json..
                        if not json_object:
                            # write what we have (data variable) to an event
                            self.write_event_to_stream(stream, name, str(data))

                        if json_object:
                            # if json is valid ParameterData write ParameterData
                            if name == "ParameterData":
                                self.write_param_data(data, stream)
                            else:
                                # otherwise, send the json object as the payload
                                self.write_event_to_stream(stream, name, str(json_object))
