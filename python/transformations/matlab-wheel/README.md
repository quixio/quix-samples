# Matlab Wheel

This code sample demonstrates how to run MATLAB functions in Quix as Python-compatible .whl packages.

It builds on `containers.mathworks.com/matlab-runtime:r2024b` instead of the standard `python:3.13-slim-trixie` because the compiled MATLAB code needs the MATLAB Runtime, and installs Python 3.12 on it, the newest version the R2024b wheel supports.

## How to build the wheel

### 01 - Your MATLAB function
- Ensure you understand the types and number of inputs and outputs of your function. 
- Save your .m function file in the compilation-files folder (like the rot.m example).

### 02 - Compile for Quix
Let's compile the MATLAB function using the Quix compiler:  
- Open MATLAB from the **compilation-files** folder.  
- Run the `quix_compiler.m` script, replacing the arguments:  
  ```matlab
  quix_compiler('function_name', 'py')
  ```
This will generate a folder named py containing the Python-compatible code, as well as the .whl package that we’ll deploy to Quix.

### 03 - Update the .whl in the quix app
Replace the existing .whl file in your Quix app with the new one you just built.
⚠️ If the new filename differs from the previous one, make sure to update `requirements.txt` and the `COPY` line in the `dockerfile` accordingly.

### 04 - Update main.py
Edit the `matlab_processing` function in `main.py` to accommodate your specific function's input and output variables.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **output**: Name of the output topic to write to.
- **CONSUMER_GROUP**: Name of the Kafka consumer group.
- **AGREE_TO_MATLAB_RUNTIME_LICENSE**: Set to `yes` to accept the [MathWorks MATLAB Runtime license](https://www.mathworks.com/help/compiler/get-matlab-runtime-container.html). By setting it, you, the deployer, accept that license.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.