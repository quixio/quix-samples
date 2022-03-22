from quixstreaming import EventData, ParameterData, ParameterValueType, \
    StreamReader, ParameterDefinition, EventDefinition, StreamEndType
import paho.mqtt.client as paho
import traceback
from typing import List
from datetime import datetime


class HiveMQFunction:
    topic_root = 'not_set'

    def __init__(self, input_stream: StreamReader, topic_root, hivemq_client: paho.Client, stream_id: str):
        self.input_stream = input_stream
        self.hivemq_client = hivemq_client
        self.topic_root = topic_root
        self.stream_id = stream_id

    def on_stream_closed_handler(self, end_type: StreamEndType):
        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/StreamEnd/Type",
                                   payload=end_type.__str__(), qos=1)
        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/StreamEnd/DateTime",
                                   payload=datetime.utcnow().__str__(), qos=1)

    def stream_properties_changed(self):
        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/Properties/Name",
                                   payload=self.input_stream.properties.name, qos=1)

        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/Properties/Parents",
                                   payload=','.join(self.input_stream.properties.parents), qos=1)

        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/Properties/Location",
                                   payload=self.input_stream.properties.location, qos=1)

        for key, val in self.input_stream.properties.metadata.items():
            self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                       "/Properties/Metadata/" + key,
                                       payload=val, qos=1)

        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                   "/Properties/TimeOfRecording",
                                   payload=str(self.input_stream.properties.time_of_recording), qos=1)

    def on_parameter_definitions_changed_handler(self):
        def send_parameters(params: List[ParameterDefinition], level):
            for parameter in params:
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Name",
                                           payload=parameter.name, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Location",
                                           payload=parameter.location, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Id",
                                           payload=parameter.id, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Format",
                                           payload=parameter.format, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Unit",
                                           payload=parameter.unit, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/Description",
                                           payload=parameter.description, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/CustomProperties",
                                           payload=parameter.custom_properties, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/MinimumValue",
                                           payload=parameter.minimum_value, qos=1)

                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/ParameterDefinition/MaximumValue",
                                           payload=parameter.maximum_value, qos=1)

        send_parameters(self.input_stream.parameters.definitions, 0)

    def on_event_definitions_changed_handler(self):
        def print_events(params: List[EventDefinition], level):
            for event in params:
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/Name",
                                           payload=event.name, qos=1)
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/Description",
                                           payload=event.description, qos=1)
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/Id",
                                           payload=event.id, qos=1)
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/CustomProperties",
                                           payload=event.custom_properties, qos=1)
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/Location",
                                           payload=event.location, qos=1)
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id +
                                           "/EventDefinition/Level",
                                           payload=event.level.__str__(), qos=1)

        print_events(self.input_stream.events.definitions, 0)

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):

        try:
            # send the event tags
            for tag, val in data.tags.items():
                self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/EventTags/" + tag,
                                           payload=val, qos=1)

            # send the event
            self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/EventData/" + data.id,
                                       payload=str(data.value), qos=1)

        except Exception as e:
            print(e)
            traceback.print_exc()

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        try:
            # loop the timestamps in the data
            for ts in data.timestamps:
                # send the tags
                for tag, val in ts.tags.items():
                    self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/ParameterTags/" + tag,
                                               payload=val, qos=1)

                # send the parameters
                for a, p in ts.parameters.items():
                    if p.type == ParameterValueType.String:
                        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/ParameterData/String",
                                                   payload=p.string_value, qos=1)
                    if p.type == ParameterValueType.Numeric:
                        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/ParameterData/Numeric",
                                                   payload=p.numeric_value, qos=1)
                    if p.type == ParameterValueType.Binary:
                        self.hivemq_client.publish(self.topic_root + "/" + self.stream_id + "/ParameterData/Binary",
                                                   payload=p.binary_value, qos=1)

        except Exception as e:
            print(e)
            traceback.print_exc()
