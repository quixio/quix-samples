# Test file for the transformation pipeline
from quixstreams import Application
from quixstreams.sources import Source
import uuid

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

from main import define_pipeline
from utils import assert_messages_match


class TestDataSource(Source):


    memory_allocation_data = [
        {"m": "mem", "host": "host1", "used_percent": 64.56, "time": 1577836800000000000},
        {"m": "mem", "host": "host2", "used_percent": 71.89, "time": 1577836801000000000},
        {"m": "mem", "host": "host1", "used_percent": 63.27, "time": 1577836803000000000},
        {"m": "mem", "host": "host2", "used_percent": 73.45, "time": 1577836804000000000},
        {"m": "mem", "host": "host1", "used_percent": 62.98, "time": 1577836806000000000},
        {"m": "mem", "host": "host2", "used_percent": 74.33, "time": 1577836808000000000},
        {"m": "mem", "host": "host1", "used_percent": 65.21, "time": 1577836810000000000},
        # Dummy messages to close the last window (timestamp far in future)
        {"m": "mem", "host": "host1", "used_percent": 0.0, "time": 1577836820000000000},
        {"m": "mem", "host": "host2", "used_percent": 0.0, "time": 1577836820000000000},
    ]

    def run(self):
        data = iter(self.memory_allocation_data)
        # either break when the app is stopped, or data is exhausted
        while self.running:
            try:
                event = next(data)
                event_serialized = self.serialize(key=event["host"], value=event)
                self.produce(key=event_serialized.key, value=event_serialized.value)
            except StopIteration:
                print("Source finished producing messages.")
                return


def test():
    # Expected output: windowed count results based on input data
    # Input data has timestamps (in ms): 1577836800000, 1577836801000, 1577836803000,
    # 1577836804000, 1577836806000, 1577836808000, 1577836810000
    # With 3000ms (3 second) tumbling windows starting at epoch 0, windows are:
    # [1577836800000, 1577836803000), [1577836803000, 1577836806000),
    # [1577836806000, 1577836809000), [1577836809000, 1577836812000), ...
    expected_rows = [
        {"_key": "host1", "start": 1577836800000, "end": 1577836803000, "value": 1},  # Window 1: host1 event at 800
        {"_key": "host2", "start": 1577836800000, "end": 1577836803000, "value": 1},  # Window 1: host2 event at 801
        {"_key": "host1", "start": 1577836803000, "end": 1577836806000, "value": 1},  # Window 2: host1 event at 803
        {"_key": "host2", "start": 1577836803000, "end": 1577836806000, "value": 1},  # Window 2: host2 event at 804
        {"_key": "host1", "start": 1577836806000, "end": 1577836809000, "value": 1},  # Window 3: host1 event at 806
        {"_key": "host2", "start": 1577836806000, "end": 1577836809000, "value": 1},  # Window 3: host2 event at 808
        {"_key": "host1", "start": 1577836809000, "end": 1577836812000, "value": 1},  # Window 4: host1 event at 810
    ]

    app = Application(consumer_group=str(uuid.uuid4()))

    # Here instead of topic, we connect mocked data source. We give it random name
    # so it will always create new topic that is empty.
    sdf = app.dataframe(source=TestDataSource(str(uuid.uuid4())))

    # Load the pipeline definition from main file.
    sdf = define_pipeline(sdf)
    
    # Run the application (count=8 includes the dummy message that closes the last window)
    result = app.run(timeout=5, count=8, metadata=True)

    # Assert messages match expected output
    assert_messages_match(result, expected_rows)


if __name__ == "__main__":
    test()
