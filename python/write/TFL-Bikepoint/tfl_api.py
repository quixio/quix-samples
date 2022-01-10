import pandas as pd
import numpy as np
import requests

# app_id: Listed in profile section as primary key (https://api-portal.tfl.gov.uk/profile)
app_id = '{}'.format(os.environ["tfl_primary_key"])

# app_key: Listed in profile section as secondary key (https://api-portal.tfl.gov.uk/profile)
app_key = '{}'.format(os.environ["tfl_secondary_key"])

if app_id == '' or app_key == '':
    raise ValueError('Please update app_id and app_key in tfl_api.py')


url_all_bike_points = "https://api.tfl.gov.uk/BikePoint?app_id={}&app_key={}".format(app_id, app_key)


def get_agg_bikepoint_data():

    # Request using requests library
    response_all = requests.get(url_all_bike_points)

    # Inspect some attributes of the `requests` repository
    json_response_all = response_all.json()

    # Create dataframe
    df = pd.DataFrame()
    for i in range(len(json_response_all)):
        # id
        df_i = pd.DataFrame()
        df_i["i"] = [int(json_response_all[i]['id'].split("_")[1])]
        df_i["id"] = [json_response_all[i]['id']]
        df_i["Name"] = [json_response_all[i]['commonName']]
        df_i["PlaceType"] = [json_response_all[i]['placeType']]
        df_i["lat"] = [json_response_all[i]['lat']]
        df_i["lon"] = [json_response_all[i]['lon']]
        
        # Numbers
        for j in range(len(json_response_all[i]['additionalProperties'])):
            if json_response_all[i]['additionalProperties'][j]['key'] == 'NbBikes':
                df_i["NbBikes"] = [int(json_response_all[i]['additionalProperties'][j]['value'])]
            elif json_response_all[i]['additionalProperties'][j]['key'] == 'NbEmptyDocks':
                df_i["NbEmptyDocks"] = [int(json_response_all[i]['additionalProperties'][j]['value'])]
            elif json_response_all[i]['additionalProperties'][j]['key'] == 'NbDocks':
                df_i["NbDocks"] = [int(json_response_all[i]['additionalProperties'][j]['value'])]
        df = df.append(df_i)
        
    df = df.set_index('i', drop=True)
    df.sort_index(ascending=True, inplace=True)
    df = df[df['PlaceType'] == 'BikePoint'].drop('PlaceType', axis=1)
    
    # Add all BikePoints' data
    df_agg = df[['NbBikes', 'NbEmptyDocks', 'NbDocks']].sum().reset_index().set_index('index').T

    return df, df_agg
