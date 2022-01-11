# Threshold alert

This python project performs rolling window operations. 
- The predetermined is function is the mean (moving average). 
- Any other aggregation function can be inputed (by editing the rolling_function in rolling_function.py).
- The window can be defined as a time period or as a number of observations

## Environment Variables

The different environment variables to populate are:

- **input**: Input topic with the original raw signal values
- **output**: Output topic where the alarm data will be populated
- **ParameterName**: Parameter in the input topic of the specific signal that we want to apply the rolling function to
- **WindowType**: Rolling window length type. You can define the WindowType environment variable as one the following three options:
  - "Number of Observations": this will define the rolling window length with the number of last observations that we want to take into account.
  - "Time Period": this will define the rolling window length with the last time period that we want to take into account.
  - "None": the window will be an expanding one (all historic data will be taken into account). 
- **WindowValue**: Defines the window length. Depending on WindowType, the WindowValue is defined as:
  - If WindowType=="Number of Observations", WindowValue must be an integer (number of last observations).
  - If WindowType=="Time Period", WindowValue must be a [pd.Timedelta](https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.html)'s value (previous time period). See the link to learn the different units allowed and examples: ‘W’, ‘D’, ‘T’, ‘S’, ‘L’, ‘U’, ‘N’, ‘days’, ‘day’, ‘hours’, ‘hour’, ‘hr’, ‘h’, ‘minutes’, ‘minute’, ‘min’, ‘m’, ‘seconds’, ‘second’, ‘sec’, ‘milliseconds’, ‘millisecond’, ‘millis’, ‘milli’, ‘microseconds’, ‘microsecond’, ‘micros’, ‘micro’, ‘nanoseconds’, ‘nanosecond’, ‘nanos’, ‘nano’, ‘ns’. Some examples would be: "5seconds", "500milli", "2min".
  - If WindowType=="None", WindowValue="None".

That is, this is the expected format for WindowValue depending on the value of WindowType:
| WindowType             | WindowValue |
|------------------------|-------------|
| Number of Observations | 100         |
| Time Period            | 45sec       |
| None                   | None        |
