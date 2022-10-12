# Purpose
The purpose of the local docker setup is to create a temporary environment which can be used to test code or environment changes without affecting your host machine. You can use it to change your codebase, but any environment change, such as package install would have to be manually added to your dockerfile.


# Installation

You need to have installed these prerequisities to run the system. 

 * Docker (tested on version 20.10.17)
 * Docker Compose (tested on version 1.29.2)

### Install Docker ( step 1 )

You need to install Docker in your environment. 
You can do so by following this guide: https://docs.docker.com/get-docker/.

### Install Docker-Compose ( step 2 )

You need to install the Docker Compose in your environment. 
You can do so by follow this guide: https://docs.docker.com/compose/install/.

# Running the application

### Setup

Copy `docker` folder and `docker-compose.yaml` to your application's root.

### Build and run

Open a new console/terminal in your application's root, where you copied `docker-compose.yaml` in previous step.

You can start the build by running the docker compose file.

```
docker-compose run --rm server
```

This step may take some time the first time, future runs should not cause rebuild.

Using the docker file provided, you should now be in a running server, which has all requirements installed for Quix. As the running image is nothing more than the `quixpythonbaseimage` with your code folder mounted at `/app`, in order to get your application working, you'll need to install your python requirements.

You can do this using the following, executed in the `/app` folder
```
python3 -m pip install -r requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/
```

Use the resulting environment as you would your own machine, such as run your python application by executing `python3 main.py`

Note: Any file change will reflect in the original folder.

### Additional configuration
As your environment variables will greatly depend on what your application needs, make sure to update `docker/.env` as needed. By default all values are placeholder and this might be something you need to configure before application can correctly run. Several of these environment values could be considered "secrets", therefore be mindful of what you end up committing to your repository.