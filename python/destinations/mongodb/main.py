# import Utility modules
import os
import json
from typing import Union, Any, Callable, Optional
from functools import reduce, partial

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.community.mongodb import MongoDBSink, MongoQueryFilter
from quixstreams.sinks.base.item import SinkItem

# LOCAL DEV ONLY: load env vars from .env file using load_dotenv('your/file/path.env')
# from dotenv import load_dotenv
# load_dotenv()


# --------------- environment helper functions ---------------
# These handle the transition between the MongoDBSink and connector by
# parsing environment variables.

def get_kwargs_defaults() -> dict[str, Any]:
    """
    Gets the default kwargs of MongoDBSink so they can be passed in instances where
    the user did not provide an environment variable.
    """
    init_method = MongoDBSink.__init__
    kwargs_defaults = {}
    if default_kwargs_names := init_method.__defaults__:
        arg_names = init_method.__code__.co_varnames[1:]
        defaults_start_index = len(arg_names) - len(default_kwargs_names)
        for i, default_value in enumerate(default_kwargs_names):
            kwargs_defaults[arg_names[defaults_start_index + i]] = default_value
    return kwargs_defaults


def _as_bool(value: Union[str, bool]) -> bool:
    """
    Parse boolean-based kwargs.
    """
    if isinstance(value, bool):
        return value
    return value.lower() == "true"


def replace_query_refs(data):
    """
    Replaces query values like "__value.x.y.z" with a corresponding callable on a BatchItem.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            replace_query_refs(value)
        elif isinstance(value, str) and value.startswith("__"):
            thing, *keys = value[2:].split(".")
            data[key] = lambda item: reduce(lambda d, k: d[k], keys, getattr(item, thing))


def process_query_item(query: dict, item: SinkItem) -> dict:
    """
    Evaluate each query callable with a given BatchItem.
    """
    d = {}
    for k, v in query.items():
        if isinstance(v, dict):
            d[k] = process_query_item(v, item)
        elif callable(v):
            d[k] = v(item)
        else:
            d[k] = v
    return d


def document_matcher_env_parser() -> Optional[Callable[[SinkItem], MongoQueryFilter]]:
    """
    Enables passing an environment variable for MongoDBSink's document_matcher.
    If populated, parses the environment variable and converts it to usable query.
    """
    if not (document_query := os.getenv("MONGODB_DOCUMENT_MATCHER", None)):
        return document_query
    document_query = json.loads(document_query)
    replace_query_refs(document_query)
    return partial(process_query_item, document_query)


# --------------- Application Configuration ---------------


# Create our Application - see documentation for description of various settings
app = Application(
    consumer_group=os.getenv("CONSUMER_GROUP_NAME", "quixstreams-mongodb-sink"),
    auto_offset_reset="earliest",
    commit_every=int(os.getenv("BUFFER_SIZE", "1000")),
    commit_interval=float(os.getenv("BUFFER_DELAY", "1"))
)

# Use app to specify ingress topic
input_topic = app.topic(os.environ["input"])


# --------------- Sink Configuration ---------------


kwargs_defaults = get_kwargs_defaults()
mongodb_sink = MongoDBSink(
    # required settings
    url=os.environ["MONGODB_URL"],
    db=os.environ["MONGODB_DB"],
    collection=os.environ["MONGODB_COLLECTION"],
    # optional settings (have defaults)
    update_method=os.getenv("MONGODB_UPDATE_METHOD", kwargs_defaults["update_method"]),
    upsert=_as_bool(os.getenv("MONGODB_UPSERT", kwargs_defaults["upsert"])),
    document_matcher=document_matcher_env_parser() or kwargs_defaults["document_matcher"],
    add_message_metadata=_as_bool(os.getenv("MONGODB_ADD_MESSAGE_METADATA", kwargs_defaults["add_message_metadata"])),
    add_topic_metadata=_as_bool(os.getenv("MONGODB_ADD_TOPIC_METADATA", kwargs_defaults["add_topic_metadata"])),
)


# --------------- SDF Configuration ---------------

sdf = app.dataframe(input_topic)
# sdf.print() - can use this to view incoming messages
sdf.sink(mongodb_sink)


# --------------- Run Application ---------------

if __name__ == "__main__":
    app.run(sdf)
