import quixstreams as qx
from netatmo_auth_helper import NetatmoAuthHelper
import time
import os
import requests
import json
import urllib.parse
from threading import Thread

# should the main loop run?
run = True

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open the output topic where to write data out
producer_topic = client.get_topic_producer(os.environ["output"])

auth_helper = NetatmoAuthHelper(
    os.environ["client_id"], 
    os.environ["client_secret"],
    os.environ["username"],
    os.environ["password"])

def get_data():
    while run:

        token = auth_helper.get_token()

        device_id = os.environ["device_id"]

        url = "https://api.netatmo.com/api/getstationsdata?device_id={0}&get_favorites=false".format(urllib.parse.quote_plus(device_id))
                
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        
        if response.status_code >= 300:
            print("ERROR: " + response.content.decode(encoding="utf8"))
            return
        
        response_body = response.content
        response_json = json.loads(response_body.decode("utf-8"))

        devices = response_json["body"]["devices"]

        for device in devices:
            device_id = device["_id"]

            stream = producer_topic.get_or_create_stream(device_id)
            stream.properties.name = device["home_name"]

            country = device["place"]["country"]
            city = device["place"]["city"]

            stream.properties.location = "{0}/{1}".format(country, city) 

            dashboard_data = device["dashboard_data"]

            time_utc = dashboard_data["time_utc"]
            temperature = dashboard_data["Temperature"]
            co2 = dashboard_data["CO2"]
            humidity = dashboard_data["Humidity"]
            noise = dashboard_data["Noise"]
            pressure = dashboard_data["Pressure"]
            absolute_pressure = dashboard_data["AbsolutePressure"]
            temp_trend = dashboard_data["temp_trend"]
            pressure_trend = dashboard_data["pressure_trend"]

            stream.timeseries.buffer.add_timestamp_nanoseconds(time_utc * 1000000000) \
                .add_tag("country", country) \
                .add_tag("city", city ) \
                .add_value("temperature", temperature) \
                .add_value("co2", co2) \
                .add_value("humidity", humidity) \
                .add_value("noise", noise) \
                .add_value("pressure", pressure) \
                .add_value("absolute_pressure", absolute_pressure) \
                .add_value("temp_trend", temp_trend) \
                .add_value("pressure_trend", pressure_trend) \
                .publish()

            print("Device {0} telemetry sent.".format(device_id))

            for module in device["modules"]:
                name = module["module_name"]
                battery_percent = module["battery_percent"]
                reachable = module["reachable"]
                firmware = module["firmware"]
                last_seen = module["last_seen"]
                battery_vp = module["battery_vp"]
            
                dashboard_data = module["dashboard_data"]

                time_utc = dashboard_data["time_utc"]
                temperature = dashboard_data["Temperature"]
                humidity = dashboard_data["Humidity"]
                temp_trend = dashboard_data["temp_trend"]

                stream.timeseries.buffer.add_timestamp_nanoseconds(time_utc * 1000000000) \
                    .add_tag("country", country) \
                    .add_tag("city", city ) \
                    .add_value(name + "-temperature", temperature) \
                    .add_value(name + "-humidity", humidity) \
                    .add_value(name + "-temp_trend", temp_trend) \
                    .publish()

                print("Module {0} telemetry sent.".format(name))

        time.sleep(300)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()