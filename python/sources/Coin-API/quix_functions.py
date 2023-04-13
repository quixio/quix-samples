import quixstreams as qx
from dateutil import parser


class QuixFunctions:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def data_handler(self, rows, primary_currency):
        for row in rows:
            # For every currency we send value.
            self.stream_producer.timeseries.buffer.add_timestamp(parser.parse(row['time'])) \
                .add_value("{0}-{1}".format(primary_currency, row['asset_id_quote']), row['rate']) \
                .publish()

            print("{0}-{1}: {2}".format(primary_currency, row['asset_id_quote'], row['rate']))
