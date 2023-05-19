import quixstreams as qx
from weather_API import perform_API_request, get_current_weather, get_tomorrow_weather
from datetime import datetime
import time
from datetime import timezone
import traceback
from threading import Thread
import os


# should the main loop run?
run = True

api_token = "{}".format(os.environ["api_token"])

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open the output topic where to write data out
print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# CREATE A STREAM: A stream is a collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream("NY-Real-Time-Weather")
# Give the stream human-readable name. This name will appear in data catalogue.
stream_producer.properties.name = "New York Weather Real Time"
# Save stream in specific folder in data catalogue to help organize your workspace.
stream_producer.properties.location = "/NY_Real_Time"

def get_data():
    
    int_sec = 0

    while run:
        try:
            # Current timestamp
            current_time = datetime.now(timezone.utc)

            # ToL API Request
            json_response = perform_API_request(api_token)

            print(json_response)
            
            df_now = get_current_weather(json_response)
            df_1d = get_tomorrow_weather(json_response)
            list_dfs = [df_now, df_1d]

            # Write Data to Stream
            for i, forecast_time in enumerate(['Current', 'NextDay']):
                stream_producer.timeseries.buffer.add_timestamp(current_time) \
                    .add_tag('Forecast', forecast_time) \
                    .add_value('feelslike_temp_c', float(list_dfs[i].loc[0, 'feelslike_temp_c'])) \
                    .add_value('wind_kph', float(list_dfs[i].loc[0, 'wind_kph'])) \
                    .add_value('condition', list_dfs[i].loc[0, 'condition']) \
                    .publish()

            # How long did the Request and transformation take
            current_time_j = datetime.now(timezone.utc)
            int_sec = int((current_time_j - current_time).seconds)
            print(current_time, current_time_j, int_sec)

        except Exception:
            print(traceback.format_exc())

        finally:
            # We sleep for 120 seconds, so we don't reach free account limit.
            # Stop sleeping if process termination requested
            sleeping = 0
            while sleeping <= (120 - int_sec) and run:
                sleeping = sleeping + 1
                time.sleep(1)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()