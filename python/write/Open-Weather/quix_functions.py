from quixstreaming import StreamWriter


class QuixFunctions:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, current_time, list_dfs):
        # Write Data to Stream
        for i, forecast_time in enumerate(['Current', 'NextDay']):
            self.stream_writer.parameters.buffer.add_timestamp(current_time) \
                .add_tag('Forecast', forecast_time) \
                .add_value('feelslike_temp_c', list_dfs[i].loc[0, 'feelslike_temp_c']) \
                .add_value('wind_kph', list_dfs[i].loc[0, 'wind_mps'] * 3.6) \
                .add_value('condition', list_dfs[i].loc[0, 'condition']) \
                .write()
