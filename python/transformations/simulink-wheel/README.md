# Simulink Wheel

This code sample demonstrates how to run Simulink models in Quix as Python-compatible .whl packages.

It builds on `containers.mathworks.com/matlab-runtime:r2024b` instead of the standard `python:3.13-slim-trixie` because the compiled Simulink model needs the MATLAB Runtime, and installs Python 3.12 on it, the newest version the R2024b wheel supports.

## How to build the wheel

### 01 - Modify Your Simulink Model
- Create one **Inport** block per input signal. The port numbers define the input order.
- Add **Outport** blocks for the signals you want to output.
- Configure **Data Import/Export** settings:
  - **Load from workspace**: all options **unchecked**
  - **Save to workspace or file**:
    - ✅ Output → saved as `yout`
    - ✅ Data stores → saved as `dsmout`
    - ✅ Single simulation output → saved as `out`
- Save the model after applying these settings.

### 02 - Wrap the Simulink Model in a MATLAB function
- Save your Simulink model file in the `aux-files` folder (like the rot.m example).
- Open MATLAB from the `aux-files` folder.
- Open `simulink_wrapper.m` and set the `mdl` variable (first line) to your Simulink model's name.
- Create an `inputMatrix`, e.g. `[0, x1, x2, ..., xn]`, where `x1` is the value for Inport 1, and so on, as explained in step 01.  
  Example: `inputMatrix = [0, 1, 1, pi/2]`
- Run `simulink_wrapper(inputMatrix)` to compile and test the model. Make sure the output order is as expected.

### 03 - Compile for Quix
Now that the Simulink model is wrapped inside a MATLAB function, you can compile it using the Quix compiler.
- Run the `quix_compiler.m` script, replacing the arguments:  
  ```matlab
  quix_compiler('simulink_wrapper', 'py')
  ```
This will generate a folder named py containing the Python-compatible code, as well as the .whl package that we’ll deploy to Quix.

### 04 - Update the .whl in the quix app
Replace the existing .whl file in your Quix app with the new one you just built.
⚠️ If the new filename differs from the previous one, make sure to update `requirements.txt` and the `COPY` line in the `dockerfile` accordingly.

### 05 - Update main.py
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