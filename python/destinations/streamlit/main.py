import multiprocessing
import os
import sys
import threading

from streamlit.web import cli as stcli

from app import conf, store
from app import http_server
from app.streaming import start_quixstreams


def start_streamlit(port: int = conf.STREAMLIT_PORT):
    sys.argv = ["streamlit", "run", "streamlit_file.py", f"--server.port={port}"]
    sys.exit(stcli.main())


if __name__ == "__main__":
    state_store = store.StreamStateStore()

    # Start http server
    server_worker = threading.Thread(
        target=http_server.serve,
        kwargs={"port": conf.HTTP_SERVER_PORT, "state_store": state_store},
    )
    server_worker.daemon = True
    server_worker.start()

    # Start Streamlit process
    streamlit_worker = multiprocessing.Process(target=start_streamlit)
    streamlit_worker.start()

    # Start streaming data from Quix
    try:
        start_quixstreams(
            topic_name=os.environ["input"],
            state_store=state_store,
        )
    finally:
        streamlit_worker.terminate()
