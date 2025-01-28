import os
import datetime
import json
from flask import Flask, request, Response, redirect
from flasgger import Swagger
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

logger = get_logger()

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/", methods=['GET'])
def redirect_to_swagger():
    return redirect("/apidocs/")

@app.route("/data/", methods=['POST'])
def post_data_without_key():
    """
    Post data without key
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            key:
              type: string
    responses:
      200:
        description: Data received successfully
    """
    data = request.json

    logger.debug(f"{data}")

    producer.produce(topic.name, json.dumps(data))

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route("/data/{key}", methods=['POST'])
def post_data_with_key(key: str):
    """
    Post data with key
    ---
    parameters:
      - in: path
        name: key
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            key:
              type: string
    responses:
      200:
        description: Data received successfully
    """
    data = request.json

    logger.debug(f"{data}")

    producer.produce(topic.name, json.dumps(data), key.encode())

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':    
    serve(app, host="0.0.0.0", port=80)