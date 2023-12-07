import asyncio
import json
import os
import uuid

import pandas as pd
import quixstreams as qx
import websockets

# track the connections to our websocket
websocket_connections = []
websocket_connections_events = []
websocket_connections_timeseries = []


def on_dataframe_received_handler(_: qx.StreamConsumer, df: pd.DataFrame):
    global websocket_connections, websocket_connections_timeseries

    # check for and remove closed connections
    websocket_connections = [ws for ws in websocket_connections if ws.open]
    websocket_connections_timeseries = [ws for ws in websocket_connections_timeseries if ws.open]

    # Convert the 'timestamp' column to a datetime object
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ns')

    # Convert the datetime object to a UTC timestamp
    df['datetime'] = df['datetime'].dt.tz_localize('UTC')

    if len(websocket_connections) + len(websocket_connections_timeseries) > 0:
        for _, row in df.iterrows():
            data = row.to_json()
            websockets.broadcast(websocket_connections, data)
            websockets.broadcast(websocket_connections_timeseries, data)


def on_event_received_handler(_: qx.StreamConsumer, event: qx.EventData):
    global websocket_connections, websocket_connections_events

    # check for and remove closed connections
    websocket_connections = [ws for ws in websocket_connections if ws.open]
    websocket_connections_events = [ws for ws in websocket_connections_events if ws.open]

    if len(websocket_connections_events) + len(websocket_connections) > 0:
        data = json.dumps(
            {
                "id": event.id,
                "timestamp": event.timestamp.timestamp(),
                "content": event.value,
                "tags": event.tags
            }
        )
        websockets.broadcast(websocket_connections_events, data)
        websockets.broadcast(websocket_connections, data)


# this is the handler for new data streams on the broker
def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    # connect the data handler
    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received_handler
    stream_consumer.events.on_data_received = on_event_received_handler


# handle new websocket connections
async def handle_websocket(websocket, path):
    # Store the WebSocket connection for later use
    print(f"Client connected to socket. Path={path}")

    if path.endswith("/events"):
        print("Client connected to events socket")
        websocket_connections_events.append(websocket)
    elif path.endswith("/timeseries"):
        print("Client connected to timeseries socket")
        websocket_connections_timeseries.append(websocket)
    else:
        websocket_connections.append(websocket)

    i = len(websocket_connections) + len(websocket_connections_events) + len(websocket_connections_timeseries)
    print(F"{i} active connection{'s'[:i ^ 1]}")

    try:
        # Keep the connection open and wait for messages if needed
        print("Keep the connection open and wait for messages if needed")
        await websocket.wait_closed()
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client {path} disconnected normally.")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client {path} disconnected with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Remove the connection from the list when it's closed
        print("Removing client from connection list")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


# start the server. Listen on port 80
async def start_websocket_server():
    print("listening for websocket connections..")
    server = await websockets.serve(handle_websocket, '0.0.0.0', 80)
    await server.wait_closed()


# Main function to run the application
async def main():
    # Quix client
    client = qx.QuixStreamingClient()
    # the topic consumer, configured to read only the latest data
    topic_consumer = client.get_topic_consumer(
        topic_id_or_name=os.environ["input"],
        consumer_group="websocket-" + str(uuid.uuid4()),
        auto_offset_reset=qx.AutoOffsetReset.Latest)

    # connect the stream received handler
    topic_consumer.on_stream_received = on_stream_received_handler

    # subscribe to data arriving at the topic_consumer
    topic_consumer.subscribe()

    # start the server
    await start_websocket_server()

    topic_consumer.unsubscribe()


# Run the application
asyncio.run(main())

