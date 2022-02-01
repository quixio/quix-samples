from quixstreaming import SecurityOptions, StreamingClient, StreamReader
from quixstreaming.models import ParameterData, EventData, StreamEndType
import threading
import signal
import math
import datetime
import time
from PIL import Image

# Create a client. Client helps you to create input reader or output writer for specified topic.
certificatePath = "../certificates/ca.cert"
username = "{placeholder:broker.security.username}"
password = "{placeholder:broker.security.password}"
broker = "{placeholder:broker.address}"

security = SecurityOptions(certificatePath, username, password)


# Switch to UDP style communication by ignoring acks
properties = {
    "acks": "0"
}

client = StreamingClient(broker,
                         security,
                         properties)

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")
input_topic = client.open_input_topic('{placeholder:inputTopic}', "default-consumer-group-1")
output_topic = client.open_output_topic('{placeholder:outputTopic}')

all_pixels = None
img = None


def set_track(track_name):
    global img
    global all_pixels

    img = Image.open('images/{}'.format(track_name), 'r')
    all_pixels = list(img.getdata())


def keep_car_on_canvas(car_coordinates):
    canvas_width = 1280
    canvas_height = 720

    canvas_top = 0
    canvas_bottom = canvas_height
    canvas_left = 0
    canvas_right = canvas_width

    print("x:{}, y:{}".format(car_coordinates.x, car_coordinates.y))

    if car_coordinates.y <= canvas_top:
        car_coordinates.y = canvas_bottom - 5

    if car_coordinates.y >= canvas_bottom:
        car_coordinates.y = canvas_top + 5

    if car_coordinates.x < canvas_left:
        car_coordinates.x = canvas_right

    if car_coordinates.x > canvas_right:
        car_coordinates.x = canvas_left

    return car_coordinates


def get_is_on_grass(car_coordinates):
    coordinate = car_coordinates.x, car_coordinates.y

    try:
        pixel_data = img.getpixel(coordinate)
        print(pixel_data)
    except IndexError:
        return True

    if pixel_data[0] == 60:
        print("track={}, on grass={} color={}".format(img.filename, True, pixel_data[0]))
        return True
    else:
        print("track={}, on grass={} color={}".format(img.filename, False, pixel_data[0]))
        return False


def get_speed(speed, throttle, brake, is_on_grass):
    if is_on_grass:
        if throttle == 0 and brake == 0:
            if speed > 0.3:
                speed -= 0.1
            if speed < -0.3:
                speed += 0.1

    if throttle > 0:
        if not is_on_grass and speed <= 5:
            # slow down fast
            if speed < 0:
                speed += throttle / 25
            # accelerate slow
            speed += throttle / 100

        if is_on_grass:
            if speed < 0.3:
                speed += 0.1
            # on grass with throttle on, slow down
            if speed > 0.3:
                speed -= 0.1

    if brake > 0:
        if not is_on_grass and speed >= -3:
            # slow down fast
            if speed > 0:
                speed -= brake / 25
            # accelerate slow
            speed -= brake / 100

        if is_on_grass:
            if speed > -0.3:
                speed -= 0.1
            # on grass with brake on, speed up
            if speed < -0.3:
                speed += 0.1

    return speed


# Callback called for each incoming stream
def read_stream(new_stream: StreamReader):
    # Create a new stream to output data
    stream_writer = output_topic.create_stream(new_stream.stream_id + "-control")

    stream_writer.properties.parents.append(new_stream.stream_id)

    buffer = new_stream.parameters.create_buffer("steering", "throttle", "brake")

    speed = 0
    angle = 0
    start_x = 600
    start_y = 600

    car_coordinates = type('obj', (object,), {'x': start_x, 'y': start_y})
    last_timestamp = 0

    on_grass = False

    # Callback triggered for each new data frame
    def on_parameter_data_handler(data: ParameterData):
        nonlocal speed
        nonlocal angle
        nonlocal last_timestamp
        nonlocal on_grass
        nonlocal car_coordinates

        for row in data.timestamps:
            if last_timestamp > 0 and last_timestamp - row.timestamp_nanoseconds > 0:
                print("Skipped")
                continue

            if last_timestamp == 0:
                last_timestamp = row.timestamp_nanoseconds - 20000000

            throttle = row.parameters["throttle"].numeric_value
            brake = row.parameters["brake"].numeric_value
            steering = row.parameters["steering"].numeric_value

            car_coordinates = keep_car_on_canvas(car_coordinates)
            on_grass = get_is_on_grass(car_coordinates)
            speed = get_speed(speed, throttle, brake, on_grass)

            angle += ((row.timestamp_nanoseconds - last_timestamp) / 10000000) * steering * math.pi / 180

            car_coordinates.x += speed * ((row.timestamp_nanoseconds - last_timestamp) / 10000000) * math.sin(angle)
            car_coordinates.y -= speed * ((row.timestamp_nanoseconds - last_timestamp) / 10000000) * math.cos(angle)

            data = ParameterData()
            data.add_timestamp(datetime.datetime.utcnow()) \
                .add_tags(row.tags) \
                .add_value("x", car_coordinates.x) \
                .add_value("y", car_coordinates.y) \
                .add_value("speed", speed) \
                .add_value("angle", angle)

            stream_writer.parameters.write(data)
            last_timestamp = row.timestamp_nanoseconds

    # React to new data received from input topic.
    buffer.on_read += on_parameter_data_handler

    def on_event(data: EventData):
        if data.id == "track":
            set_track(data.value)

    new_stream.events.on_read += on_event

    # When input stream closes, we close output stream as well.
    def on_stream_close(end_type: StreamEndType):
        stream_writer.close(end_type)
        print("Stream closed:" + stream_writer.stream_id)

    new_stream.on_stream_closed += on_stream_close

    # React to any metadata changes.
    def stream_properties_changed():
        if new_stream.properties.name is not None:
            stream_writer.properties.name = new_stream.properties.name + " car game input"

    new_stream.properties.on_changed += stream_properties_changed


set_track("track1.png")

# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream
input_topic.start_reading()  # initiate read

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Below code is to handle graceful exit of the model.
event = threading.Event()


def signal_handler(sig, frame):
    # dispose the topic(s) and close the stream(s)
    input_topic.dispose()
    output_topic.dispose()

    print("Setting termination flag")
    event.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while not event.is_set():
    time.sleep(1)

print("Exiting")
