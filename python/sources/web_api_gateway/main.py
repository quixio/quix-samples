import os
import datetime
import json
from flask import Flask, request, Response
from waitress import serve

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

logger = get_logger()

app = Flask(__name__)


@app.route("/data/", methods=['POST'])
def post_data():
    
    data = request.json

    print(data)

    logger.info("CONNECTED: data received.")
    
    logger.info(f"{str(datetime.datetime.utcnow())} posted.")
    producer.produce(topic.name, json.dumps(data), "hello-world-stream")

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    
    print("-------------------------CURL EXAMPLE-------------------------")
    print(f"curl -X POST -H 'Content-Type: application/json' -d '{{\"key\": \"value\"}}' {service_url}/data")
    serve(app, host="0.0.0.0", port=80)