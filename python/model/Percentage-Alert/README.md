# Percentage Alert

This python project generates an alert when certain percentage increase or decrease is achieved. 
- The percentage value is inserted in percentage points: 20 = 20%.
- It automatically updates last relative minima and maxima data values.

![Percentage_Alert](PercentageAlert.png?raw=true)

## Environment Variables

The different environment variables to populate are:

- **input**: Input topic with the original raw signal values
- **output**: Output topic where the alarm data will be populated
- **ParameterName**: Parameter in the input topic of the specific signal that we want to apply the alert to
- **PercentagePointsAlert**: Percentage points that the signal has to vay for the alert to activate. 10 = 10%, 20=20%, etc.
