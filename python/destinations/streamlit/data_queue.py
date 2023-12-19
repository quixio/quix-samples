import time
import threading
from queue import Queue
from threading import Lock, Thread

# This class manages communication between the data source (Kafka) and
# streamlit.
class DataQueue:
    def __init__(self, maxlen=0) -> None:

        # Removes resources associated with inactive client connections (e.g., closed browser tabs)
        def _clean_up_queues(connections: {}, lock: Lock):
            while True:
                active_c = set([x.ident for x in threading.enumerate()])
                inactive_c = []
                for t in connections:
                    if t not in active_c:
                        inactive_c.append(t)
                if len(inactive_c) > 0:
                    with lock:
                        for key in inactive_c:
                            connections.pop(key)
                time.sleep(30)

        self.connections = {}
        self.maxlen = maxlen
        self.lock = Lock()
        self.cleanup_thread = Thread(target=_clean_up_queues, args=(self.connections, self.lock))
    
    def start(self):
        self.cleanup_thread.start()

    def get(self, key: int, block=True, timeout=None):
        if key not in self.connections:
            self.connections[key] = Queue(self.maxlen)
        return self.connections[key].get(block, timeout)
    
    def put(self, item, block=True, timeout=None):
        with self.lock:
            for _, v in self.connections.items():
                v.put(item, block, timeout)
