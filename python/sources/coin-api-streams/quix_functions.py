import quixstreams as qx
from dateutil import parser


class QuixFunctions:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def data_handler(self, base, quote, time, rate):
        self.stream_producer.timeseries.buffer \
            .add_timestamp(parser.parse(time)) \
            .add_value("BASE_CURRENCY", base) \
            .add_value("QUOTE_CURRENCY", quote) \
            .add_value("PRICE", rate) \
            .publish()

        print(f"{time}: {base}/{quote} price: {rate}")
