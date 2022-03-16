import pandas as pd
 
class RollingWindow:

    def __init__(self, window_type: str, window_value: str):
        self.df_window = pd.DataFrame()


        # Define window out of WindowType and WindowValue environmental variables
        if window_type == 'Number of Observations':
            self.window = int(window_value)
        elif window_type == 'Time Period':
            self.window = pd.Timedelta(str(window_value))
        else:
            self.window = None

    
    def append(self, new_df: pd.DataFrame()):
        df = new_df.copy()
        df.loc['time'] = df['time'].apply(lambda x: pd.Timestamp(x))   # Correct time format to pd.Timestamp()
        self.df_window = self.df_window.append(df)  # Update df_window

        # Apply window
        if type(self.window) == int:
            self.df_window = self.df_window.iloc[-self.window:, :]
        if type(self.window) == pd.Timedelta:
            min_date = self.df_window['time'].iloc[-1] - self.window
            self.df_window = self.df_window[self.df_window['time'] > min_date]