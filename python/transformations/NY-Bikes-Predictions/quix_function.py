from quixstreaming import StreamWriter
from model_functions import get_saved_models, predict_bikes_availability_and_write_into_streams
import pandas as pd


class QuixFunction:
    # Get saved models
    dic_ml_model_1h, dic_ml_model_1d = get_saved_models()

    # Create empty dataframes for bikes and weather data
    df_bikes = pd.DataFrame()
    df_weather = pd.DataFrame()

    def __init__(self, bike_stream: StreamWriter, prediction_1h_stream_writer: StreamWriter,
                 prediction_1d_stream_writer: StreamWriter):
        self.bike_stream = bike_stream
        self.prediction_1h_stream_writer = prediction_1h_stream_writer
        self.prediction_1d_stream_writer = prediction_1d_stream_writer

    def on_bike_parameter_data_handler(self, df: pd.DataFrame):
        self.df_bikes = df.copy(deep=True)

        # each time new data arrives, predict the bike availability
        self.run_prediction()

    def on_weather_parameter_data_handler(self, df: pd.DataFrame):
        self.df_weather = df.copy(deep=True)

        # each time new data arrives, predict the bike availability
        self.run_prediction()

    def run_prediction(self):
        # run the prediction with the latest bike and weather data
        predict_bikes_availability_and_write_into_streams(self.df_bikes, self.df_weather,
                                                          self.dic_ml_model_1h,
                                                          self.dic_ml_model_1d, self.bike_stream,
                                                          self.prediction_1h_stream_writer,
                                                          self.prediction_1d_stream_writer)
