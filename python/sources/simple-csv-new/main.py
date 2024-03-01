import os

from connector import CsvSourceConnector

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

csv_source_connector = CsvSourceConnector(
    csv_path=os.path.join(script_dir, "demo-data.csv"),
    topic_name="csv_transaction_data",
    default_broker_address="localhost:9092",
    key_parser="AccountId"
)

if __name__ == "__main__":
    csv_source_connector.run()