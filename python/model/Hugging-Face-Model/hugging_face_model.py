from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
from transformers import pipeline
import pandas as pd
import os


class HuggingFaceModel:
    # Initiate
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.model = pipeline(model = os.environ["HuggingFaceModel"])

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        # Get fresh input data
        df = data.to_panda_frame()

        # Get the data to pass to the model. Yo may do any processing here.
        # For this example, we select the 'text' column from the input data
        predict_in = df['text'][0]

        # Model prediction
        response = self.model(predict_in)

        # Get label (check response format first for each hugging face model)
        label = response[0]['label']
        score = response[0]['score']

        # Add label and score to input data dataframe
        df['PredictedLabel'] = label
        df['PredictedScore'] = score

        # Show that this is working in the console by printing
        print(label, score, predict_in)

        # Write df to output stream
        self.output_stream.parameters.write(df)
