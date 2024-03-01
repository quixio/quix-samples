import logging
from quixstreams.logging import LogLevel, _DEFAULT_HANDLER, _DEFAULT_FORMATTER


def setup_logging(
    logger: logging.Logger = logging.getLogger("connector"),
    loglevel: LogLevel = 'INFO'
):
    logger.setLevel(loglevel)
    _DEFAULT_HANDLER.setFormatter(_DEFAULT_FORMATTER)
    _DEFAULT_HANDLER.setLevel(loglevel)
    logger.addHandler(_DEFAULT_HANDLER)