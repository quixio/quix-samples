from quixstreaming import EventData, ParameterData, ParameterValueType
import paho.mqtt.client as paho
import traceback


class HiveMQFunction:
    topic_root = 'not_set'

    def __init__(self, topic_root, hivemq_client: paho.Client):
        self.hivemq_client = hivemq_client
        self.topic_root = topic_root

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):

        try:
            # send the event tags
            for tag, val in data.tags.items():
                self.hivemq_client.publish(self.topic_root + "/event_tags/" + tag, payload=val, qos=1)

            # send the event
            self.hivemq_client.publish(self.topic_root + "/event/" + data.id, payload=str(data.value), qos=1)

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
                    self.hivemq_client.publish(self.topic_root + "/parameter_tags/" + tag, payload=val, qos=1)

                # send the parameters
                for a, p in ts.parameters.items():
                    if p.type == ParameterValueType.String:
                        self.hivemq_client.publish(self.topic_root + "/parameter/string", payload=p.string_value, qos=1)
                    if p.type == ParameterValueType.Numeric:
                        self.hivemq_client.publish(self.topic_root + "/parameter/numeric", payload=p.numeric_value, qos=1)
                    if p.type == ParameterValueType.Binary:
                        self.hivemq_client.publish(self.topic_root + "/parameter/binary", payload=p.binary_value, qos=1)

        except Exception as e:
            print(e)
            traceback.print_exc()