import quixstreams as qx
from model_functions import get_saved_models, predict_bikes_availability_and_write_into_streams
import pandas as pd


class QuixFunction:
    # Get saved models
    dic_ml_model_1h, dic_ml_model_1d = get_saved_models()

    # Create empty dataframes for bikes and weather data
    df_bikes = pd.DataFrame()
    df_weather = pd.DataFrame()

    def __init__(self, bike_stream: qx.StreamProducer, prediction_1h_stream_producer: qx.StreamProducer,
                 prediction_1d_stream_producer: qx.StreamProducer):
        self.bike_stream = bike_stream
        self.prediction_1h_stream_producer = prediction_1h_stream_producer
        self.prediction_1d_stream_producer = prediction_1d_stream_producer

    def on_bike_parameter_data_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        self.df_bikes = df.copy(deep = True)

        # each time new data arrives, predict the bike availability
        self.run_prediction()

    def on_weather_parameter_data_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        self.df_weather = df.copy(deep = True)

        # each time new data arrives, predict the bike availability
        self.run_prediction()

    def run_prediction(self):
        # run the prediction with the latest bike and weather data
        predict_bikes_availability_and_write_into_streams(self.df_bikes, self.df_weather,
                                                          self.dic_ml_model_1h,
                                                          self.dic_ml_model_1d, self.bike_stream,
                                                          self.prediction_1h_stream_producer,
                                                          self.prediction_1d_stream_producer)
