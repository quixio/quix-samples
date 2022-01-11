import requests
import pandas as pd

from datetime import datetime, timezone
import pytz


def perform_API_request(openweather_api_key):
    # NY Location
    NY_location = [40.7128, 74.0060]
    lat = NY_location[0]
    lon = NY_location[1]

    # API call setup
    exclude = "minutely"
    units = 'metric'

    # Url definition
    url_ny_weather = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&units={}&appid={}".format(
        lat, lon, exclude, units, openweather_api_key)

    # Request API using requests library
    response = requests.get(url_ny_weather)

    # Convert to json
    json_response = response.json()

    return json_response


def get_current_weather(json_response):
    # Create dataframe
    df = pd.DataFrame()
    df['feelslike_temp_c'] = [json_response['current']['feels_like']]
    df['wind_mps'] = [json_response['current']['wind_speed']]
    df['condition'] = [json_response['current']['weather'][0]['main']]

    return df


def get_tomorrow_weather(json_response):
    # Create dataframe
    df = pd.DataFrame()
    df['feelslike_temp_c'] = [json_response['hourly'][24]['feels_like']]
    df['wind_mps'] = [json_response['hourly'][24]['wind_speed']]
    df['condition'] = [json_response['hourly'][24]['weather'][0]['main']]

    return df