from quixstreaming import StreamWriter
from dateutil import parser


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, rows, from_currency):
        for row in rows:
            # For every currency we send value.
            self.stream_writer.parameters.buffer.add_timestamp(parser.parse(row['time'])) \
                .add_value("{0}-{1}".format(from_currency, row['asset_id_quote']), row['rate']) \
                .write()

            print("{0}-{1}: {2}".format(from_currency, row['asset_id_quote'], row['rate']))
