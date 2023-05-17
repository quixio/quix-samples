import cherrypy

from .store import StreamStateStore

__all__ = ("serve",)


class Server:
    def __init__(self, state_store: StreamStateStore):
        self._state_store = state_store

    @cherrypy.expose
    def index(self):
        return self._state_store.to_csv_bytes()


def serve(port: int, state_store: StreamStateStore):
    """
    Launch a simple HTTP server to serve the streaming data for Streamlit
    :param port: Port number
    :param state_store: stream state store with the records to serve for Streamlit
    """
    cherrypy.config.update(
        {
            "server.socket_host": "localhost",
            "server.socket_port": port,
            "environment": "embedded",
            "log.screen": False,
            "log.access_file": "",
            "log.error_file": "",
        }
    )

    cherrypy.quickstart(Server(state_store=state_store))
