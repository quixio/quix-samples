import time
import requests
import json
import datetime

class NetatmoAuthHelper:

    def __init__(self, client_id: str, client_secret: str, username: str, password: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._token = None

    def get_token(self) -> str:
        if self._token is None:
            self._get_token()
            
        if time.time() - self._expire_in > 0:
            self._get_refresh_token()

        return self._token
            

    def _get_refresh_token(self):
        payload = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._refresh_token
        }

        response = requests.post("https://api.netatmo.com/oauth2/token", data = payload)

        print(str(response.content))

        response_body = json.loads(response.content)
        self._token = response_body["access_token"]
        self._refresh_token = response_body["refresh_token"]
        self._expire_in = time.time() + response_body["expires_in"]

        print("Refresh token acquired with validation until " + str(datetime.datetime.utcfromtimestamp(self._expire_in)))


    def _get_token(self):
        payload = {
            "grant_type": "password",
           "client_id": self._client_id,
            "client_secret": self._client_secret,
            "username": self._username,
            "password": self._password
        }

        response = requests.post("https://api.netatmo.com/oauth2/token", data = payload)

        

        response_body = json.loads(response.content)
        self._token = response_body["access_token"]
        self._refresh_token = response_body["refresh_token"]
        self._expire_in = time.time() + response_body["expires_in"]

        print("Token acquired with validation until " + str(datetime.datetime.utcfromtimestamp(self._expire_in)))




