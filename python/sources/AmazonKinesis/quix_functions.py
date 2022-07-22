from quixstreaming import StreamWriter, EventData
from datetime import datetime
import traceback

class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def write_data(self, data) -> None:
            
        print("Sending RAW data event to Quix")

        try:
            event_data = EventData(event_id="raw_data", time=datetime.utcnow(), value=str(data))
            self.stream_writer.events.write(event_data)
        except BaseException:
            print(traceback.format_exc())
