import requests
import pandas as pd
from datetime import datetime, timedelta


def perform_API_request(api_token):

    date_from = datetime.today().strftime('%Y-%m-%d')
    date_to = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')
    location = 'NewYorkCity'

    response = requests.request('GET', f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date_from}/{date_to}?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cname%2Cfeelslike%2Cwindspeed%2Cwindspeedmean%2Cconditions%2Cdescription%2Cicon&include=days%2Cfcst&key={api_token}&contentType=json')
    if response.status_code != 200:
        print('Unexpected Status code: ', response.status_code)

    # Convert to json
    json_data = response.json()

    print(u'Current temperature in %s is %d℃' % (json_data['address'], json_data['days'][0]['feelslike']))
    print(u'Tomorrows temperature in %s is %d℃' % (json_data['address'], json_data['days'][1]['feelslike']))

    return json_data


def get_current_weather(json_response):
    # Create dataframe
    df = pd.DataFrame()
    df['feelslike_temp_c'] = [json_response['days'][0]['feelslike']]
    df['wind_kph'] = [json_response['days'][0]['windspeed']]
    df['condition'] = [json_response['days'][0]['description']]

    return df


def get_tomorrow_weather(json_response):
    # Create dataframe
    df = pd.DataFrame()
    df['feelslike_temp_c'] = [json_response['days'][1]['feelslike']]
    df['wind_kph'] = [json_response['days'][1]['windspeed']]
    df['condition'] = [json_response['days'][1]['description']]

    return df