# Rolling Window Function

This python project performs rolling window operations. 
- The predetermined function is the mean (moving average). 
- Any other aggregation function can be inputed (by editing the rolling_function in rolling_function.py).
- The window can be defined as a time period or as a number of observations

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for the windowed data.
- **ParameterName**: The stream's parameter to perform the window function upon.
- **WindowType**: Rolling window length type. Can be defined as one the following three options:
  - ***"Number of Observations"***: Defines the rolling window length with the number of last observations to take into account.
  - ***"Time Period"***: Defines the rolling window length with the last time period to take into account.
  - ***"None"***: Defines the window to be expanding (all historic data will be taken into account). 
- **WindowValue**: Defines the window length. Depending on WindowType, the WindowValue is defined as:
  - If WindowType == "Number of Observations", WindowValue must be an integer (number of last observations).
  - If WindowType == "Time Period", WindowValue must be a [pd.Timedelta](https://pandas.pydata.org/docs/reference/api/pandas.Timedelta.html) value. 
    
    See the link to learn about the different units allowed and examples: * *‘W’, ‘D’, ‘T’, ‘S’, ‘L’, ‘U’, ‘N’, ‘days’, ‘day’, ‘hours’, ‘hour’, ‘hr’, ‘h’, ‘minutes’, ‘minute’, ‘min’, ‘m’, ‘seconds’, ‘second’, ‘sec’, ‘milliseconds’, ‘millisecond’, ‘millis’, ‘milli’, ‘microseconds’, ‘microsecond’, ‘micros’, ‘micro’, ‘nanoseconds’, ‘nanosecond’, ‘nanos’, ‘nano’, ‘ns’* *. 
    
    Some examples of correct WindowValues would be: "5seconds", "500milli", "2min".
  - If WindowType == "None", WindowValue="None".
  
In summary, this is an example of the expected format for WindowValue depending on the value of WindowType:
| WindowType             | WindowValue |
|------------------------|-------------|
| Number of Observations | 100         |
| Time Period            | 45sec       |
| None                   | None        |


## Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](/python/local-development) how to setup your local environment.


