# Install dependencies
You have the option of installing dependencies via script or manually.

##  Install dependencies via script
In this folder you will find `quix-dependency-installer-mac.sh`, which installs all necessary requirements.
To run it, copy-paste the following into a terminal:
```
chmod +x ./quix-dependency-installer-mac.sh && ./quix-dependency-installer-mac.sh
```

## Install dependencies manually
### Python
Currently tested to work with [3.8.7](https://www.python.org/downloads/release/python-387/), but other python versions of 3.7 and 3.8 are expected to also work.


### Install and configure PythonNet dependencies
- Install Brew package manager (from brew.sh). You might have to add it to the path manually, in that case run 
    ```
    echo "export PATH=/usr/local/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile && echo "Worked" || echo "Failed"
    ```
    or on M1 chips:    
    ```
    echo "export PATH=/opt/homebrew/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile && echo "Worked" || echo "Failed"
    ```
- Install rosetta if on M1
    ```
    sudo softwareupdate --install-rosetta --agree-to-license
    ```
- Install Mono Version
    ```
    curl https://download.mono-project.com/archive/6.12.0/macos-10-universal/MonoFramework-MDK-6.12.0.122.macos10.xamarin.universal.pkg -O
    monoPkgPath=./MonoFramework-MDK-6.12.0.122.macos10.xamarin.universal.pkg
    sudo installer -pkg $monoPkgPath -target /
    echo "export PATH=/Library/Frameworks/Mono.framework/Versions/Current/Commands:$PATH" >> ~/.bash_profile && source ~/.bash_profile && echo "Worked" || echo "Failed"
    echo "export PKG_CONFIG_PATH=/Library/Frameworks/Mono.framework/Versions/Current/lib/pkgconfig:$PKG_CONFIG_PATH" >> ~/.bash_profile && source ~/.bash_profile && echo "Worked" || echo "Failed"
    ```
- Install pip for python if you don't already have it
    ```
    curl https://bootstrap.pypa.io/get-pip.py --output ./get-pip.py
    python3 downloads/get-pip.py
    ```
- Additional things to install:
    ```
    brew install pkg-config
    python3 -m pip install wheel
    python3 -m pip install pycparser
    ```

### Create new python environment
We highly suggest to use a python virtual environment, as the Quix streaming package currently relies on some dll redirecting, which is achieved by adding a file to your python environment. This is done automatically, but to avoid any complication with other python applications you might want to use relying on similar techniques, a virtual environment is advised.
Make sure your terminal is using the correct python version by executing
```
python3 --version
```
If the version is not what you expect, do
```
export PATH=/Library/Frameworks/Python.framework/Versions/3.8/bin:$PATH
```


To create a new virtual environment, execute the following in a terminal at your desired location:
```
python3 -m pip install virtualenv
python3 -m virtualenv env --python=python3.8
chmod +x ./env/bin/activate
source ./env/bin/activate
```
You will know you succeeded in activating the environment if your terminal line starts with (env). Future steps will assume you have the virtual environment activated or happy to install into global python.

### Install samples requirements
In the same terminal you activated the virtual environment, navigate to the folder where `requirements.txt` is located and execute
```
python3 -m pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/
```

# Run the sample
In the same terminal you activated the virtual environment, navigate to the folder where `main.py` is located and execute
```
python3 main.py
```