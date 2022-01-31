from quixstreaming import ParameterData


class QuixFunction:

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        df = data.to_panda_frame()
        print(df.to_string())
