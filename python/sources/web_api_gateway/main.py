import os
import datetime
import json
from flask import Flask, request, Response
from waitress import serve
import time

from setup_logging import get_logger

from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

quix_app = Application()
topic =  quix_app.topic(os.environ["output"])
producer = quix_app.get_producer()

portal_api = os.environ["Quix__Portal__Api"]
workspace_id = os.environ["Quix__Workspace__Id"]
service_url = portal_api.replace("portal-api.dev", f"gateway-{workspace_id}.deployments-dev")

validated = False

logger = get_logger()

app = Flask(__name__)


@app.route("/data/", methods=['POST'])
def post_data_without_key():
    
    data = request.json

    logger.debug(f"{data}")

    if not validated:
        logger.info("Message received.")
        time.sleep(1)        
        logger.info("CONNECTED!")
    
    producer.produce(topic.name, json.dumps(data))

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/data/{key}", methods=['POST'])
def post_data_with_key(key: str):
    
    data = request.json

    logger.debug(f"{data}")

    if not validated:
        logger.info("Message received.")
        time.sleep(1)        
        logger.info("CONNECTED!")
    
    producer.produce(topic.name, json.dumps(data), key.encode())

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    
    print("=" * 60)
    print(" " * 20 + "CURL EXAMPLE")
    print("=" * 60)
    print(
        f"""
curl -X POST \\
    -H 'Content-Type: application/json' \\
    -d '{{"key": "value"}}' \\
    {service_url}/data
    """
    )
    print("=" * 60)  
    
    
    serve(app, host="0.0.0.0", port=80)