from quixstreaming import StreamWriter
from dateutil import parser


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, base, quote, time, rate):
        self.stream_writer.parameters.buffer \
            .add_timestamp(parser.parse(time)) \
            .add_value("BASE_CURRENCY", base) \
            .add_value("QUOTE_CURRENCY", quote) \
            .add_value("PRICE", rate) \
            .write()

        print(f"{time}: {base}/{quote} price: {rate}")
