# Percentage alert

This python project generates an alert when certain percentage increase or decrease is achieved. 
- It works at both sides of the threshold. 
- The signal value doesn't need to be equal to the threshold value for the alarm to go off.
- It keeps activating when the threshold is crossed (doesn't stop after it goes off the first time).

![Threshold_Alert](Threshold_Alert.png?raw=true)

## Environment Variables

The different environment variables to populate are:

- **input**: Input topic with the original raw signal values
- **output**: Output topic where the alarm data will be populated
- **ParameterName**: Parameter in the input topic of the specific signal that we want to apply the threshold to
- **ThresholdValue**: Threshold's numerical value
