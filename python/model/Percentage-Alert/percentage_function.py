from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd

# Initiate global variables
global_max = None
global_max_ti = None
global_min = None
global_min_ti = None
  
class PercentageAlert:
    # Initiate
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter, parameter_name:str, perc_points_alert:float):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.parameter_name = parameter_name
        self.perc_points_alert = perc_points_alert

    # Is it the signal value lower or higher than the threshold value?
    def update_global_max_and_min(signal_value, ti, max_dif_min_max):
        global global_max, global_min, global_max_ti, global_min_ti
        # Update global_max
        if global_max == None:
            global_max = signal_value
            global_max_ti = ti
        elif signal_value > global_max:
            global_max = signal_value
            global_max_ti = ti
            # If global_max is updated, update global_min too if it's now too far below
            if abs((global_max-global_min)/global_min) > max_dif_min_max:
                global_min = global_min + max_dif_min_max*(global_max-global_min)
                global_min_ti = ti     
        # Update global_min
        if global_min == None:
            global_min = signal_value
            global_min_ti = ti
        elif signal_value < global_min:
            global_min = signal_value
            global_min_ti = ti
            # If global_min is updated, update global_max too if it's too far above
            if abs((global_max-global_min)/global_min) > max_dif_min_max:
                global_max = global_max - max_dif_min_max*(global_max-global_min)
                global_max_ti = ti


    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

     # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        global global_max, global_min, global_max_ti, global_min_ti
        
        # Get fresh data
        df = data.to_panda_frame()
        ti = pd.Timestamp(df.loc[0,'time'])
        signal_value = float(df.loc[0,self.parameter_name])
        print(signal_value)
        
        # Update global max and min variables
        max_dif_min_max = (self.perc_points_alert*1.5)/100
        PercentageAlert.update_global_max_and_min(signal_value, ti, max_dif_min_max)
        
        # Alert if change is bigger than perc_alert: INCREASE
        if abs((signal_value - global_min)/global_min) > self.perc_points_alert/100:
            # Generate alert data parameters
            df['Alert'] = str(self.perc_points_alert)+"% increase"
            df[self.parameter_name+'_previous_low_value'] = global_min
            df[self.parameter_name+'_previous_low_value_time'] = global_min_ti
            cols = ['time', self.parameter_name, 'Alert', self.parameter_name+'_previous_low_value', self.parameter_name+'_previous_low_value_time']
            self.output_stream.parameters.buffer.write(df[cols])  # Send alert data to output topic
            
            # Update global max
            global_max = signal_value
            global_max_ti = ti
            global_min = signal_value
            global_min_ti = ti

            print()
            print()
            print()
            print("ALARM")
            print(df[cols])
            print()
            print()
            print()
        
        # Alert if change is bigger than perc_alert: DECREASE
        elif abs((global_max - signal_value)/signal_value) > self.perc_points_alert/100:
            # Generate alert data parameters
            df['Alert'] = str(self.perc_points_alert)+"% decrease"
            df[self.parameter_name+'_previous_high_value'] = global_max
            df[self.parameter_name+'_previous_high_value_time'] = global_max_ti
            cols = ['time', self.parameter_name, 'Alert', self.parameter_name+'_previous_high_value', self.parameter_name+'_previous_high_value_time']
            self.output_stream.parameters.buffer.write(df[cols])  # Send alert data to output topic
            
            # Update global max
            global_max = signal_value
            global_max_ti = ti
            global_min = signal_value
            global_min_ti = ti
            
            print()
            print()
            print()
            print("ALARM")
            print(df[cols])
            print()
            print()
            print()        