from quixstreaming import StreamWriter


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, current_time_i, total_bikes, df_i_agg):
        # Write Data to Stream
        self.stream_writer.parameters.buffer.add_timestamp(current_time_i) \
            .add_value('total_num_bikes_available', total_bikes) \
            .add_value('num_docks_available', df_i_agg.loc[0, 'num_docks_available']) \
            .write()