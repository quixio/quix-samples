# MATLAB

Use this template to deploy transformations that use MATLAB and Simulink. 

## Requirements

To create Python packages from MATLAB functions you need the following MathWorks products
 - MATLAB
 - MATLAB Compiler
 - MATLAB Compiler SDK 

To create Python packages from Simulink products, in addition to the above list, you also need
 - Simulink
 - Simulink Compiler

## Environment variables
 - `INPUT_TOPIC`: Kafka topic to receive input data from.
 - `OUTPUT_TOPIC`: Kafka topic to write the results of the transformation.

## Preparing Python packages from MATLAB and Simulink

Package your MATLAB and Simulink assets as a Python package using the MATLAB compiler SDK. Upload the resulting package (package directory that contains the `__init__.py` and a `*.ctf` file, `pyproject.toml` and `setup.py`) to the `MATLAB` directory in this template.

## Resources for MATLAB Compiler SDK and MATLAB Runtime APIs

 - [Call MATLAB functions from Python](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html?s_tid=CRUX_lftnav)
 - [MATLAB Arrays in Python](https://www.mathworks.com/help/matlab/matlab_external/matlab-arrays-as-python-variables.html)
 - [Pass data to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-python.html)
 - [MATLAB Compiler SDK reference](https://www.mathworks.com/help/compiler/mcc.html#d124e20858)
 - [Calling Simulink from Python](https://github.com/mathworks/Call-Simulink-from-Python)