# Simulink

Use this template to deploy Simulink models to Quix. Upload your *.slx files containing Simulink model with any other assets required to run the model to the MATLAB directory of this project. Use MATLAB workspace variables send input signals based on Quix Streams to the simulink model and receive output signals. The best way to do this is write a simple MATLAB function like `engine.m` in the example that receives input data from .NET, set a workspace variable, call the simulink model return output result to a MATLAB workspace variable. 

This project template contains a modified version of [simulation of a four-cylinder spark ignition internal combustion engine](https://www.mathworks.com/help/simulink/slref/modeling-engine-timing-using-triggered-subsystems.html) by MathWorks. Refer to the diagrams below to compare key differences between the IO components of the two models. The signals for throttle angle, load torque and engine speed have been converted to workspace variables:

<p float="center">
  <img src="img/img1.png" />
  <img src="img/img2.png" /> 
</p>

Following links contain useful information about using the MATLAB engine for .NET:
 - [Execute MATLAB functions from .NET](https://www.mathworks.com/help/matlab/matlab_external/execute-matlab-functions-from-net.html)
 - [MATLAB Engine](https://www.mathworks.com/help/matlab/apiref/mathworks.matlab.engine.matlabengine.html#mw_ba179c55-e64b-4a3b-a091-73db6a587d62)
 - [Pass .NET data types to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-net.html)
 - [Handle MATLAB data in .NET](https://www.mathworks.com/help/matlab/matlab_external/handle-matlab-data-in-net-applications.html)

**It is recommended that you deloy MATLAB engine with at least 2 CPU and 4GB memory.**

## Requirements
 - A license server that is accessible from the Quix environment.
 - MATLAB concurrent license (standalone or named network licenses do not work).

## Build variables

 - To start MATLAB engine you must set the `MLM_LICENSE_FILE` environment variable to your license server port and URL in the `build/dockerfile` file (line 23). E.g., `MLM_LICENSE_FILE=27000@0.0.0.0`.

## Environment variable
 - `INPUT_TOPIC`: Kafka topic to receive input data from.
 - `OUTPUT_TOPIC`: Kafka topic to write the results of the transformation.