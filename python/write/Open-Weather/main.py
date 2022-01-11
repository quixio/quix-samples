from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from ny_weather_API import perform_API_request, get_current_weather, get_tomorrow_weather
from datetime import datetime
import pandas as pd
import time
from datetime import timezone
import traceback
import signal
from threading import Thread, Event

# should the main loop run?
run = True

openweather_api_key = "{}".format(os.environ["openweatherkey"])

# configure security objects
client = QuixStreamingClient('{placeholder:token}')

# Open the output topic
print("Opening output topic")
output_topic = client.open_output_topic(os.environ["output"])

# CREATE A STREAM: A stream is a collection of data that belong to a single session of a single source.
stream = output_topic.create_stream("NY-Real-Time-Weather")
# Give the stream human readable name. This name will appear in data catalogue.
stream.properties.name = "New York Weather Real Time"
# Save stream in specific folder in data catalogue to help organize your workspace.
stream.properties.location = "/NY_Real_Time"


def get_data():

    QuixFunctions.__init__(output_stream)

    while run:
        try:
            # Current timestamp
            current_time = datetime.now(timezone.utc)

            # ToL API Request
            json_response = perform_API_request(openweather_api_key)
            df_now = get_current_weather(json_response)
            df_1d = get_tomorrow_weather(json_response)
            list_dfs = [df_now, df_1d]

            # Write stream
            QuixFunctions.data_handler(current_time, list_dfs)

            # How long did the Request and transformation take
            current_time_j = datetime.now(timezone.utc)
            int_sec = int((current_time_j - current_time).seconds)
            print(current_time, current_time_j, int_sec)

            # We sleep for 30 minutes so we don't reach free account limit.
            # Stop sleeping if process termination requested
            sleeping = 0
            while sleeping <= (1800 - int_sec) and not exit_event.is_set():
                sleeping = sleeping + 1
                time.sleep(1)

        except Exception:
            print(traceback.format_exc())


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target=get_data)
    thread.start()

    App.run(before_shutdown=before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
