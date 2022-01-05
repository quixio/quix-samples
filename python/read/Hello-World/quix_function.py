from quixstreaming import ParameterData


class QuixFunction:

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(data: ParameterData):

        # print first value of ParameterA parameter if it exists
        hello_world_value = data.timestamps[0].parameters['ParameterA'].numeric_value
        if hello_world_value is not None:
            print("ParameterA - " + str(data.timestamps[0]) + ": " + str(hello_world_value))

