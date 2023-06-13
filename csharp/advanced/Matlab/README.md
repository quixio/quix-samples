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

## Preparing .NET assemblies from MATLAB and Simulink

Package your MATLAB and Simulink assets as a .NET assembly using the MATLAB compiler SDK. Upload the resulting package (`*.ctf` file) to the `MATLAB` directory in this template.

## Resources for MATLAB Compiler SDK and MATLAB Runtime APIs

 - [Execute MATLAB functions from .NET](https://www.mathworks.com/help/matlab/matlab_external/execute-matlab-functions-from-net.html)
 - [MATLAB Engine](https://www.mathworks.com/help/matlab/apiref/mathworks.matlab.engine.matlabengine.html#mw_ba179c55-e64b-4a3b-a091-73db6a587d62)
 - [Pass .NET data types to MATLAB](https://www.mathworks.com/help/matlab/matlab_external/pass-data-to-matlab-from-net.html)
 - [Handle MATLAB data in .NET](https://www.mathworks.com/help/matlab/matlab_external/handle-matlab-data-in-net-applications.html)

Following example from MathWorks has useful information on preparing a Simulink model for deployment. The project shows how to package and call the model from Python. However, the design principles of the model is equally applicable to .NET.

 - [Calling Simulink from Python](https://github.com/mathworks/Call-Simulink-from-Python)
