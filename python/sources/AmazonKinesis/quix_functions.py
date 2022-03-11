from quixstreaming import StreamWriter, EventData
from datetime import datetime


class QuixFunctions:

    is_connected = False

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def write_data(self, data) -> None:

        print("Sending RAW data event to Quix")

        event_data = EventData(event_id="raw_data", time=datetime.utcnow(), value=str(data))

        self.stream_writer.events.write(event_data)

        if not self.is_connected:
            print("CONNECTED!")
            self.is_connected = True

