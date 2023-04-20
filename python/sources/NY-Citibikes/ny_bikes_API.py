import requests
import pandas as pd


def get_agg_data():
    response_k = requests.get('https://gbfs.citibikenyc.com/gbfs/en/station_status.json')

    # Inspect some attributes of the `requests` repository
    json_response_k = response_k.json()

    # Create dataframe
    df = pd.DataFrame()

    # Iterate over stations
    for station in json_response_k['data']['stations']:
        df_i = pd.DataFrame()
        df_i["id"] = [station['station_id']]
        df_i["num_bikes_available"] = [int(station['num_bikes_available'])]
        df_i["num_docks_available"] = [int(station['num_docks_available'])]
        df_i["num_ebikes_available"] = [int(station['num_ebikes_available'])]
        df = df.append(df_i)

    df = df.set_index('id', drop = True)
    df.sort_index(ascending = True, inplace = True)

    df_agg = df.sum().reset_index().set_index('index').T

    return df_agg
