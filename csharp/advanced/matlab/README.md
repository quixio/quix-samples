# MATLAB

Use this template to deploy transformations that use MATLAB functions. Upload your *.m files containing MATLAB code to the MATLAB directory in this project. Then you can call them using MATLAB engine for .NET. The template contains an example in which a MATLAB function `rot`, which rotates a 2-D vector counter-clockwise by a specified angle, rotating vectors input via Quix Streams. Following links contain useful information about using the MATLAB engine for .NET:
 - [Execute MATLAB functions from .NET](https://www.mathworks.com/help/matlab/matlab_external/execute-matlab-functions-from-net.html)
 - [MATLAB Engine](https://www.mathworks.com/help/matlab/apiref/mathworks.matlab.engine.matlabengine.html#mw_ba179c55-e64b-4a3b-a091-73db6a587d62)
 - [Pass .NET data types to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-net.html)
 - [Handle MATLAB data in .NET](https://www.mathworks.com/help/matlab/matlab_external/handle-matlab-data-in-net-applications.html)

**It is recommended that you deloy MATLAB engine with at least 2 CPU and 4GB memory.**

## Requirements
 - A license server that is accessible from the Quix environment.
 - MATLAB concurrent license.

## Build variables

 - To start MATLAB engine you must set the MLM_LICENSE_FILE environment variable to your license server port and URL in the `build/dockerfile` file (line 23). E.g., `MLM_LICENSE_FILE=27000@0.0.0.0`.

## Environment variable
 - `INPUT_TOPIC`: Kafka topic to receive input data from.
 - `OUTPUT_TOPIC`: Kafka topic to write the results of the transformation.