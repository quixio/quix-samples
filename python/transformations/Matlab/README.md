# MATLAB

Use this template to deploy transformations that use MATLAB functions. Upload your *.m files containing MATLAB code to the MATLAB directory in this project. Then you can call them using MATLAB engine for Python. The template contains an example in which a MATLAB function `rot`, which rotates a 2-D vector counter-clockwise by a specified angle, rotating vectors input via Quix Streams. Following links contain useful information about using the MATLAB engine for Python:
 - [Call MATLAB functions from Python](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html?s_tid=CRUX_lftnav)
 - [MATLAB Arrays in Python](https://www.mathworks.com/help/matlab/matlab_external/matlab-arrays-as-python-variables.html)
 - [Pass data to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-python.html)

**It is recommended that you deloy MATLAB engine with at least 2 CPU and 4GB memory.**

## Requirements
 - A license server that is accessible from the Quix environment.
 - MATLAB concurrent license (standalone or named network licenses do not work).

## Build variables

 - To start MATLAB engine you must set the MLM_LICENSE_FILE environment variable to your license server port and URL in the `build/dockerfile` file (line 23). E.g., `MLM_LICENSE_FILE=27000@0.0.0.0`.

## Environment variable
 - `INPUT_TOPIC`: Kafka topic to receive input data from.
 - `OUTPUT_TOPIC`: Kafka topic to write the results of the transformation.