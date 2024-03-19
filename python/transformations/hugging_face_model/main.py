import os
from quixstreams import Application, State
from transformers import pipeline

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix("hugging-face-model-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

# Download the Hugging Face model (list of available models here: https://huggingface.co/models)
# suggested default is distilbert-base-uncased-finetuned-sst-2-english
model_name = os.environ["HuggingFaceModel"]
print("Downloading {0} model...".format(model_name))
model_pipeline = pipeline(model=model_name)

sdf = app.dataframe(input_topic)

# Assuming the input data has a 'text' column that you want to process with the model
sdf = sdf.apply(lambda row: {
    "text": row["text"],
    "sentiment": model_pipeline(row["text"])[0]  # Replace with the actual model output
})

# Send the processed data to the output topic
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)