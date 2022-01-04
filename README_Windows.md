# Python
Currently tested to work with [3.8.7](https://www.python.org/downloads/release/python-387/), but other python versions of 3.7 and 3.8 are expected to also work.

# Windows
- Install latest .Net Core runtime (https://dotnet.microsoft.com/download/dotnet-core/current/runtime)


# Create new python environment
We highly suggest to use a python virtual environment, as the Quix streaming package currently relies on some dll redirecting, which is achieved by adding a file to your python environment. This is done automatically, but to avoid any complication with other python applications you might want to use relying on similar techniques, a virtual environment is advised.

To create a new virtual environment, execute the following in a command line at your desired location:
```
pip install virtualenv
python -m virtualenv env --python=python3.8
"env/Scripts/activate"
```
You will know you succeeded in activating the environment if your command line starts with (env). Future steps will assume you have the virtual environment activated or happy to install into global python.

Note: You might need to use a new command line after installing Python, because PATH isn't refreshed for existing command lines when something is installed.

# Install samples requirements
Open a console in the folder where `requirements.txt` is located and execute
```
pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/
```

# Run the sample
## From console
In the same console you activated the virtual environment, navigate to the folder where `main.py` is located and execute
```
python main.py
```
## From PyCharm
1) File > Settings
2) Search 'interpreter', find 'Python Interpreter' under project's name (Name will be something like 'Project: 1-hello-world')
3) Click on cog icon (around top right next to a dropdown)
4) Click on Add...
5) Under 'Virtual Environment' menu options, you'll have to option to select New Environment or Existing Environment. Select Existing and set interpreter path to python.exe in the virtual environment you created
6) click OK
7) Verify the newly added interpreter is selected as Python Interpreter (dropdown next to the cog in point 3)
8) Click OK
9) Right click on main.py, "Run 'main.py'"