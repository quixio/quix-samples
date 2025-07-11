from typing import Union, Callable, Iterable, Optional
import os

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
    return os.environ.get(env_var, "false").lower() == "true"


def _as_iterable(env_var) -> list[str]:
    return keys.split(",") if (keys := os.environ.get(env_var)) else []


def _get_tdengine_subtable_name(
    tags_keys: Union[Callable[[dict], Iterable[str]], Iterable[str]]
) -> Callable[[dict], Optional[str]]:
    """
    TDengine names subtables based on each unique combination of tag values.
    By default, the names are randomized like `t_dc7d907438b41235ca431e52392ac2a4`,
    which occurs when you do not pass an explicit name (`None`).

    This allows you to instead name them something human-readable using a record's
    combined tag values, ex. `host1__USA` for tags (hostname, region).
    """
    if not _as_bool("TDENGINE_NAME_SUBTABLES_FROM_TAGS"):
        # uses names auto-generated by TDengine
        return lambda row: None

    def _subtable_name(row: dict):
        _tags_keys = tags_keys(row) if callable(tags_keys) else tags_keys
        return "__".join([str(row[tk]) for tk in _tags_keys])

    return _subtable_name


# Potential Callables - can manually edit these to instead use your own callables.
# --Required--
supertable: SupertableSetter = os.getenv("TDENGINE_SUPERTABLE")
# --Optional--
tags_keys: TagsSetter = _as_iterable("TDENGINE_TAGS_KEYS")
fields_keys: FieldsSetter = _as_iterable("TDENGINE_FIELDS_KEYS")
subtable: SubtableNameSetter = _get_tdengine_subtable_name(tags_keys)


tdengine_sink = TDengineSink(
    host=os.environ["TDENGINE_HOST"],
    database=os.environ["TDENGINE_DATABASE"],
    token=os.environ["TDENGINE_TOKEN"],
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
