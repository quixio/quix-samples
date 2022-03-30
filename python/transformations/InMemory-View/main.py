from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from in_memory_view import InMemoryView
import os

client = QuixStreamingClient()
input_topic = client.open_input_topic(os.environ["input"], "view")
output_topic = client.open_output_topic(os.environ["output"])

materialized_view = InMemoryView(input_topic, output_topic)

materialized_view.start()
App.run()