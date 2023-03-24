import quixstreams as qx
from datetime import datetime


class QuixFunctions:

    is_connected = False

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def raw_message_handler(self, msg):

        if not self.is_connected:
            # show once
            print("CONNECTED!")
            self.is_connected = True
        data = msg.value

        # print("Sending RAW data as event")
        event_data = EventData(event_id = "raw_data", time = datetime.utcnow(),
                               value = str(data, "UTF-8"))
        print(event_data)
        self.stream_producer.events.write(event_data)
