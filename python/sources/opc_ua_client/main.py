import asyncio
import logging
import os
import json
import signal
import time

from asyncua import Client, ua
from quixstreams import Application
from opc_ua_source import OpcUaSource

# keep the app running?
run = True

OPC_URL = os.environ["OPC_SERVER_URL"]

OPC_NAMESPACE = os.environ["OPC_NAMESPACE"]
TOPIC_NAME = os.environ["output"]

params_to_process = os.getenv("PARAMETER_NAMES_TO_PROCESS", '')
params_to_process = params_to_process.replace("'", "\"")
PARAMETER_NAMES_TO_PROCESS = json.loads(params_to_process)

_logger = logging.getLogger(__name__)
logging.getLogger("asyncua.common.subscription").setLevel(logging.WARNING)
logging.getLogger("asyncua.client.ua_client.UaClient").setLevel(logging.WARNING)

logging.basicConfig(level=logging.INFO)

# Create an Application
app = Application(
        consumer_group="data_source", 
        auto_create_topics=True)

opc_ua_source = OpcUaSource("opc_ua_source", OPC_URL, OPC_NAMESPACE, PARAMETER_NAMES_TO_PROCESS)

# define the topic using the "output" environment variable
topic = app.topic(TOPIC_NAME)

app.add_source(opc_ua_source, topic)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting gracefully.")