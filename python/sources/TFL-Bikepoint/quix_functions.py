import quixstreams as qx
import parser


class QuixFunctions:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def data_handler(self, df, current_time):
        # iterate over df rows (over bike points)
        for i, row in df.iterrows():
            self.stream_producer.timeseries.buffer.add_timestamp(current_time) \
                .add_tag('Id', row['id']) \
                .add_value('Name', row['Name']) \
                .add_value('Lat', row['lat']) \
                .add_value('Lon', row['lon']) \
                .add_value('NbBikes', row['NbBikes']) \
                .add_value('NbEmptyDocks', row['NbEmptyDocks']).publish()
            