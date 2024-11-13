import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import plotly.express as px
import time
import os


# InfluxDB settings
INFLUXDB_URL = os.environ["INFLUXDB_HOST"]
INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]
INFLUXDB_ORG =  os.environ["INFLUXDB_ORG"]
INFLUXDB_BUCKET = os.environ["INFLUXDB_BUCKET_NAME"]

# Streamlit title
st.title("InfluxDB Data Visualization")

# Refresh interval (in seconds)
REFRESH_INTERVAL = 10

# Main app loop
while True:

  # Connect to InfluxDB
  client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

  # Define the query (modify it to match your data structure)
  query = os.environ["INFLUXDB_QUERY"]

  # Execute the query
  tables = client.query_api().query(query)

  # Process query results into a DataFrame
  data = []
  for table in tables:
      for record in table.records:
          data.append({
              "time": record.get_time(),
              "value": record.get_value()
          })

  # Close InfluxDB client
  client.close()

  # Create a DataFrame
  df = pd.DataFrame(data)

  # Display waveform plot
  if not df.empty:
      fig = px.line(df, x="time", y="value", title="Waveform")
      st.plotly_chart(fig)

      # Display table
      st.subheader("Data Table")
      st.write(df)
  else:
      st.write("No data available for the selected time range.")

  # Refresh every REFRESH_INTERVAL seconds
  time.sleep(REFRESH_INTERVAL)
  st.rerun()