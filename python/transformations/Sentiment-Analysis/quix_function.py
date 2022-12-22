from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd
from transformers import Pipeline

class QuixFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter, classifier: Pipeline):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.classifier = classifier

        self.sum = 0
        self.count = 0

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        print("events")

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df_all_messages: pd.DataFrame):

        # Use the model to predict sentiment label and confidence score on received messages
        model_response = self.classifier(list(df_all_messages["chat-message"]))

        # Add the model response ("label" and "score") to the pandas dataframe
        df = pd.concat([df_all_messages, pd.DataFrame(model_response)], axis=1)

        # Iterate over the df to work on each message
        for i, row in df.iterrows():

            # Calculate "sentiment" feature using label for sign and score for magnitude
            df.loc[i, "sentiment"] = row["score"] if row["label"] == "POSITIVE" else - row["score"]

            # Add average sentiment (and update memory)
            self.count = self.count + 1
            self.sum = self.sum + df.loc[i, "sentiment"]
            df.loc[i, "average_sentiment"] = self.sum/self.count

        # Output data with new features
        self.output_stream.parameters.write(df)
