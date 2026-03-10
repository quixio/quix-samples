import os
import datetime
import json
import functools
from flask import Flask, request, Response, redirect
from flasgger import Swagger
from waitress import serve
import time

from flask_cors import CORS

from setup_logging import get_logger
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

service_url = os.environ["Quix__Deployment__Network__PublicUrl"]

basic_auth_username = os.environ.get("basic_auth_username")
basic_auth_password = os.environ.get("basic_auth_password")
basic_auth_enabled = bool(basic_auth_username and basic_auth_password)

api_key = os.environ.get("api_key")
api_key_enabled = bool(api_key)

auth_required = basic_auth_enabled or api_key_enabled


def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if auth_required:
            if api_key_enabled and request.headers.get("X-API-Key") == api_key:
                return f(*args, **kwargs)
            if basic_auth_enabled:
                auth = request.authorization
                if auth and auth.username == basic_auth_username and auth.password == basic_auth_password:
                    return f(*args, **kwargs)
            return Response(
                "Unauthorized", 401,
                {"WWW-Authenticate": 'Basic realm="HTTP API Source"'}
            )
        return f(*args, **kwargs)
    return decorated

quix_app = Application()
topic = quix_app.topic(os.environ["output"])
producer = quix_app.get_producer()

logger = get_logger()

app = Flask(__name__)

# Enable CORS for all routes and origins by default
CORS(app)

app.config['SWAGGER'] = {
    'title': 'HTTP API Source',
    'description': 'Test your HTTP API with this Swagger interface. Send data and see it arrive in Quix.',
    'uiversion': 3
}

swagger = Swagger(app)

@app.route("/", methods=['GET'])
def redirect_to_swagger():
    return redirect("/apidocs/")

@app.route("/data/", methods=['POST'])
@require_auth
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
            some_value:
              type: string
    responses:
      200:
        description: Data received successfully
    """
    data = request.json
    logger.debug(f"{data}")

    producer.produce(topic.name, json.dumps(data))

    # Return a normal 200 response; CORS headers are added automatically by Flask-CORS 
    return Response(status=200)

@app.route("/data/<key>", methods=['POST'])
@require_auth
def post_data_with_key(key: str):
    """
    Post data with a key
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
            some_value:
              type: string
    responses:
      200:
        description: Data received successfully
    """
    data = request.json
    logger.debug(f"{data}")

    producer.produce(topic.name, json.dumps(data), key.encode())

    return Response(status=200)

if __name__ == '__main__':
    print("=" * 60)
    print(" " * 20 + "CURL EXAMPLE")
    print("=" * 60)
    if api_key_enabled:
        auth_flag = f"\\\n    -H 'X-API-Key: {api_key}' "
    elif basic_auth_enabled:
        auth_flag = f"\\\n    -u '{basic_auth_username}:{basic_auth_password}' "
    else:
        auth_flag = ""
    print(
        f"""
curl -L -X POST {auth_flag}\\
    -H 'Content-Type: application/json' \\
    -d '{{"key": "value"}}' \\
    {service_url}/data
    """
    )
    print("=" * 60)

    serve(app, host="0.0.0.0", port=80)