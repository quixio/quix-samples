import os
import subprocess
import threading

from app import conf, store
from app import http_server
from app.streaming import start_quixstreams


def start_streamlit(port: int):
    """
    Run Streamlit as subprocess and wait for its exit.

    If OS kills streamlit with OOM, the main process will stop too.
    :param port: Streamlit server port
    """
    return subprocess.run(
        [
            "streamlit",
            "run",
            "streamlit_file.py",
            f"--server.port={port}",
        ],
        check=True,
    )


if __name__ == "__main__":
    state_store = store.StreamStateStore()

    # Start http server
    server_worker = threading.Thread(
        target=http_server.serve,
        kwargs={"port": conf.HTTP_SERVER_PORT, "state_store": state_store},
    )
    server_worker.daemon = True
    server_worker.start()

    # Start quix worker
    quix_worker = threading.Thread(
        target=start_quixstreams,
        kwargs={
            "topic_name": os.environ["input"],
            "state_store": state_store,
        },
    )
    quix_worker.daemon = True
    quix_worker.start()

    # Start streamlit in subprocess and wait
    start_streamlit(port=conf.STREAMLIT_PORT)
