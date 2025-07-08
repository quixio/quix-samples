# import Utility modules
import os

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.community.tdengine.sink import (
    TDengineSink,
    FieldsSetter,
    TagsSetter,
    SupertableSetter,
    SubtableNameSetter,
)

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


def _as_bool(env_var: str) -> bool:
    return os.environ.get(env_var, "true").lower() == "true"


def _as_iterable(env_var) -> list[str]:
    return keys.split(",") if (keys := os.environ.get(env_var)) else []


# Potential Callables - can manually edit these to instead use your own callables.
# --Required--
supertable: SupertableSetter = os.getenv("TDENGINE_SUPERTABLE")
subtable: SubtableNameSetter = os.getenv("TDENGINE_SUBTABLE")
# --Optional--
tags_keys: TagsSetter = _as_iterable("TDENGINE_TAGS_KEYS")
fields_keys: FieldsSetter = _as_iterable("TDENGINE_FIELDS_KEYS")


tdengine_sink = TDengineSink(
    host=os.environ["TDENGINE_HOST"],
    database=os.getenv("TDENGINE_DATABASE"),
    token=os.getenv("TDENGINE_TOKEN"),
    username=os.getenv("TDENGINE_USERNAME"),
    password=os.getenv("TDENGINE_PASSWORD"),
    supertable=supertable,
    subtable=subtable,
    fields_keys=fields_keys,
    tags_keys=tags_keys,
    time_key=col if (col := os.environ.get("TIMESTAMP_COLUMN")) else None,
    time_precision=os.environ["TDENGINE_TIME_PRECISION"],
    allow_missing_fields=_as_bool("TDENGINE_ALLOW_MISSING_FIELDS"),
    include_metadata_tags=_as_bool("TDENGINE_INCLUDE_METADATA_TAGS"),
    convert_ints_to_floats=_as_bool("TDENGINE_CONVERT_INTS_TO_FLOATS"),
    enable_gzip=_as_bool("TDENGINE_ENABLE_GZIP"),
)


app = Application(
    consumer_group=os.environ.get("CONSUMER_GROUP_NAME", "tdengine-data-writer"),
    auto_offset_reset="earliest",
    commit_every=int(os.environ.get("BUFFER_SIZE", "1000")),
    commit_interval=float(os.environ.get("BUFFER_DELAY", "1")),
)
input_topic = app.topic(os.environ["input"])
app.dataframe(input_topic).sink(tdengine_sink)


if __name__ == "__main__":
    app.run()
