from quixstreaming import StreamWriter
import pandas as pd
import pickle
import traceback


class QuixFunction:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer
        self.model = pickle.load(open("data/ML_model.pkl", "rb"))


    def on_pandas_frame_handler(self, cleaned_row_df: pd.DataFrame):
        #print(cleaned_row_df)
        try:
            # Run the model and get the predicted value
            cols_when_model_builds = self.model.get_booster().feature_names
            x_df = cleaned_row_df[cols_when_model_builds]
            predicted_values = self.model.predict(x_df)

            print(len(cleaned_row_df), len(predicted_values))
            if len(cleaned_row_df) == len(predicted_values):
               output_df = cleaned_row_df
               output_df["predicted_value"] = predicted_values

               self.stream_writer.parameters.write(output_df)
               self.stream_writer.parameters.flush()
        except Exception as e:
            print(e)
            traceback.print_exc()
