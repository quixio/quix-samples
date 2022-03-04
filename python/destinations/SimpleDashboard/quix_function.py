from quixstreaming import ParameterData
import pandas as pd

class QuixFunction:

    def __init__(self):
        self.dashboard = pd.DataFrame()

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        
        df = data.to_panda_frame()

        if "EngineRPM" in df.columns:
            df = df.append(self.dashboard)

            def aggregate(x: pd.Series):
                row = {
                    "time": x['time'].iloc[0],
                    "Speed": x["EngineRPM"].max(),
                    "TAG__LapNumber": x["TAG__LapNumber"].iloc[0]
                }
                return pd.Series(row)

            self.dashboard = df.groupby("TAG__LapNumber").apply(aggregate)

            #print(self.dashboard[["TAG__LapNumber", "Speed"]])



        
