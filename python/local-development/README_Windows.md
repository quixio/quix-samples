# Python
Currently tested to work with [3.8.7](https://www.python.org/downloads/release/python-387/), but other 3.7 and 3.8 Python versions are also expected to work.

# Windows
- Install the latest .Net Core runtime (https://dotnet.microsoft.com/download/dotnet-core/current/runtime).


# Create new python environment
We highly suggest using a Python virtual environment, because the Quix streaming package currently relies on some dll redirecting, which is achieved by adding a file to your Python environment. This is done automatically. You might want to rely on a similar techniques but, to avoid any complication with other Python applications, a virtual environment is advised.

To create a new virtual environment, execute the following in a command line at your desired location:
```
pip install virtualenv
python -m virtualenv env --python=python3.8
"env/Scripts/activate"
```
You will know you succeeded in activating the environment if your command line starts with (env). Future steps will assume you have the virtual environment activated or are happy to install into global Python.

Note: You might need to use a new command line after installing Python, because PATH isn't refreshed for existing command lines when something is installed.

# Install samples requirements
Open a console in the folder where `requirements.txt` is located and execute
```
pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/
```

# Run the sample
## From console
In the same console that you activated the virtual environment, navigate to the folder where `main.py` is located and execute
```
python main.py
```
## From PyCharm
1) File > Settings
2) Search 'interpreter' and find 'Python Interpreter' under project's name. The name will be something like 'Project: 1-hello-world'.
3) Click on cog icon around the top right, next to a dropdown.
4) Click on Add...
5) Under 'Virtual Environment' menu options, you'll have the option to select New Environment or Existing Environment. Select Existing Environment and set the interpreter path to python.exe in the virtual environment that you created.
6) Click OK
7) Verify the newly added interpreter is selected as Python Interpreter (in the dropdown next to the cog mentioned in setp 3).
8) Click OK
9) Right click on main.py, "Run 'main.py'".