from quixstreaming import StreamWriter, EventData
from datetime import datetime


class QuixFunctions:

    is_connected = False

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def raw_message_handler(self, msg):

        if not self.is_connected:
            # show once
            print("CONNECTED!")
            self.is_connected = True
        data = msg.value

        # print("Sending RAW data as event")
        event_data = EventData(event_id="raw_data", time=datetime.utcnow(),
                               value=str(data, "UTF-8"))
        print(event_data)
        self.stream_writer.events.write(event_data)
