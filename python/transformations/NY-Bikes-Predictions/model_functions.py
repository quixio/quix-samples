import quixstreams as qx
import base64
import pickle
import pandas as pd
from datetime import datetime, timezone, timedelta
from dateutil import tz


def get_saved_model(model_name):
    with open('./MLModels/' + model_name + ".pickle") as file:
        response_binary = base64.b64decode(file.read())
        response_pickle = pickle.loads(response_binary)

    print("Loaded model " + model_name)
    return response_pickle


def get_saved_models():
    dic_ml_model_1h = get_saved_model("ML_1h_Forecast")
    dic_ml_model_1d = get_saved_model("ML_1day_Forecast")
    return dic_ml_model_1h, dic_ml_model_1d


def get_X_predict(current_ny_time, df_weather, df_bikes):
    # Add timestamp
    df_X = pd.DataFrame({'timestamp_ny': [current_ny_time]})

    # Add current number of bikes
    df_X['total_num_bikes_available'] = int(df_bikes.loc[0, 'total_num_bikes_available'])

    # Add weather variables
    df_X['feelslike_temp_c'] = float(df_weather.loc[df_weather['TAG__Forecast'] == 'Current', 'feelslike_temp_c'])
    df_X['wind_kph'] = float(df_weather.loc[df_weather['TAG__Forecast'] == 'Current', 'wind_kph'])
    df_X['feelslike_temp_c_24'] = float(df_weather.loc[df_weather['TAG__Forecast'] == 'NextDay', 'feelslike_temp_c'])
    df_X['wind_kph_24'] = float(df_weather.loc[df_weather['TAG__Forecast'] == 'NextDay', 'wind_kph'])

    for col_i in ['condition_Clear', 'condition_Clouds', 'condition_Rain', 'condition_Snow']:
        if col_i.split('_')[-1] == str(df_weather.loc[df_weather['TAG__Forecast'] == 'Current', 'condition'][0]):
            df_X[col_i] = 1
        else:
            df_X[col_i] = 0

    for col_i in ['condition_24_Clear', 'condition_24_Clouds', 'condition_24_Rain', 'condition_24_Snow']:
        if col_i.split('_')[-1] == str(df_weather.loc[df_weather['TAG__Forecast'] == 'NextDay', 'condition'][1]):
            df_X[col_i] = 1
        else:
            df_X[col_i] = 0

    # Add time variables
    df_X['year'] = df_X['timestamp_ny'].dt.year
    df_X['month'] = df_X['timestamp_ny'].dt.month
    df_X['day'] = df_X['timestamp_ny'].dt.day
    df_X['hour'] = df_X['timestamp_ny'].dt.hour
    df_X['minute'] = df_X['timestamp_ny'].dt.minute
    df_X['dayofweek'] = df_X['timestamp_ny'].dt.dayofweek

    cols_to_return = ['timestamp_ny', 'total_num_bikes_available',
                      'wind_kph', 'feelslike_temp_c', 'wind_kph_24', 'feelslike_temp_c_24',
                      'condition_Clear', 'condition_Clouds', 'condition_Rain', 'condition_Snow',
                      'condition_24_Clear', 'condition_24_Clouds', 'condition_24_Rain', 'condition_24_Snow',
                      'year', 'month', 'day', 'hour', 'minute', 'dayofweek']

    return df_X[cols_to_return]


def generate_predictions(current_ny_time, df_bikes, df_weather, dic_ml_model_1h, dic_ml_model_1d):
    df_X = get_X_predict(current_ny_time, df_weather, df_bikes)

    ml_model_1h = dic_ml_model_1h['model']
    cols_1h = dic_ml_model_1h['variables']
    ml_model_1d = dic_ml_model_1d['model']
    cols_1d = dic_ml_model_1d['variables']

    current_n_bikes = int(df_bikes['total_num_bikes_available'][0])

    df_pred_1h = pd.DataFrame({
        'timestamp_ny': [current_ny_time + timedelta(hours = 1)],
        'timestamp_ny_execution': [str(current_ny_time)],
        'forecast_1h': [current_n_bikes + int(ml_model_1h.predict(df_X[cols_1h]))]})

    df_pred_1day = pd.DataFrame({
        'timestamp_ny': [current_ny_time + timedelta(hours = 24)],
        'timestamp_ny_execution': [str(current_ny_time)],
        'forecast_1d': [current_n_bikes + int(ml_model_1d.predict(df_X[cols_1d]))]})

    return df_pred_1h, df_pred_1day


def predict_bikes_availability_and_write_into_streams(df_bikes, df_weather, dic_ml_model_1h, dic_ml_model_1d,
                                                      bike_stream: qx.StreamProducer, 
                                                      prediction_1h_stream: qx.StreamProducer, 
                                                      prediction_1d_stream: qx.StreamProducer):
    # If any of the dataframes is empty we cannot predict, so let's check that
    if df_bikes.empty | df_weather.empty:
        return

    # Get current time in New York
    current_time = datetime.now(timezone.utc)
    current_ny_time = pd.to_datetime(current_time).astimezone(tz.gettz('America/New_York'))

    # Perform Predictions
    df_pred_1h, df_pred_1day = generate_predictions(current_ny_time, df_bikes, df_weather, dic_ml_model_1h,
                                                    dic_ml_model_1d)

    # We write in 3 different streams to define 3 different timestamps
    # Write bike_stream: real number of available bikes now
    bike_stream.timeseries.buffer.add_timestamp(current_ny_time.to_pydatetime()) \
        .add_value('timestamp_ny_execution', str(current_ny_time.to_pydatetime())) \
        .add_value('real_n_bikes', float(df_bikes.loc[0, 'total_num_bikes_available'])) \
        .publish()

    # Write prediction_1h_stream: 1 hour ahead prediction
    prediction_1h_stream.timeseries.buffer.add_timestamp(df_pred_1h.loc[0, 'timestamp_ny']) \
        .add_value('timestamp_ny_execution', df_pred_1h.loc[0, 'timestamp_ny_execution']) \
        .add_value('forecast_1h', float(df_pred_1h.loc[0, 'forecast_1h'])) \
        .publish()

    # Write prediction_1d_stream: 1 day ahead prediction
    prediction_1d_stream.timeseries.buffer.add_timestamp(df_pred_1day.loc[0, 'timestamp_ny']) \
        .add_value('timestamp_ny_execution', df_pred_1day.loc[0, 'timestamp_ny_execution']) \
        .add_value('forecast_1d', float(df_pred_1day.loc[0, 'forecast_1d'])) \
        .publish()

    # Print some predictions data
    print('NY time:', current_ny_time)
    print('Current n bikes:', int(df_bikes.loc[0, 'total_num_bikes_available']), 'Forecast 1h:',
          float(df_pred_1h.loc[0, 'forecast_1h']), 'Forecast 1 day:', float(df_pred_1day.loc[0, 'forecast_1d']))