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
 - `input`: Kafka topic to receive input data from.
 - `output`: Kafka topic to write the results of the transformation.

## Preparing Python packages from MATLAB and Simulink

`MATLAB` directory in the project has pre-compiled packages from MATLAB and Simulink assets. So, you can simply deploy and run this project. However, if you'd like to create the Python package from the source files, you can find them in the `assets` directory of this project. You can compile them using the following command:

```
mcc -W python:quixmatlab engine.m rot.m -d ../MATLAB
```

You only need the package directory that contains the `__init__.py` and a `*.ctf` file, `pyproject.toml` and `setup.py` in the `MATLAB` directory in this template.

## Resources for MATLAB Compiler SDK and MATLAB Runtime APIs

 - [Call MATLAB functions from Python](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html?s_tid=CRUX_lftnav)
 - [MATLAB Arrays in Python](https://www.mathworks.com/help/matlab/matlab_external/matlab-arrays-as-python-variables.html)
 - [Pass data to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-python.html)
 - [MATLAB Compiler SDK reference](https://www.mathworks.com/help/compiler/mcc.html#d124e20858)
 - [Calling Simulink from Python](https://github.com/mathworks/Call-Simulink-from-Python)