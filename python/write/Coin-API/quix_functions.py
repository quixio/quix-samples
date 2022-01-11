from quixstreaming import StreamWriter


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, df):

        # iterate over df rows (over bike points)
        for i, row in df.iterrows():
            self.stream_writer.parameters.buffer.add_timestamp(current_time) \
                .add_tag('Id', row['id']) \
                .add_value('Name', row['Name']) \
                .add_value('Lat', row['lat']) \
                .add_value('Lon', row['lon']) \
                .add_value('NbBikes', row['NbBikes']) \
                .add_value('NbEmptyDocks', row['NbEmptyDocks']).write()

