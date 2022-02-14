

# Installlation

You need to have installed these prerequisities to run the system. 

 * Docker (tested on version 19.03.6)
 * Docker Compose (tested on version 1.23.1)

### Install Docker ( step 1 )

You need to install Docker in your environment. 
You can do so by following this guide: https://docs.docker.com/get-docker/.

### Install Docker-Compose ( step 2 )

You need to install the Docker Compose in your environment. 
You can do so by follow this guide: https://docs.docker.com/compose/install/.

# Running the application

### Simple one-time run

You can start the build by running the docker compose file.

```
docker-compose up --build
```


### Running as a daemon in the background

If you want to run the application as a daemon in the background, you can use this command:

```
docker-compose stop && docker-compose up --build -d
```

This command to access application logs:

```
docker-compose logs -f
```

And this command to stop the application:

```
docker-compose stop
```

### Accessing the system Bash

If you want to install the new Python package or freeze current packages, you need to access the internal Bash of the Docker. First, you need to have the application started as a deamon (one step above).

Then execute:

```
docker-compose exec server bash
```


Once you are here, you can install the Python package as you are used to (e.g., `pip install YOUR_PACKAGE` or `pip freeze -r requirements.txt`).

