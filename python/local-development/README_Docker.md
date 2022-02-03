

# Installlation

In order to run the system you need to have installed these prerequisities.

 * Docker (tested on version 19.03.6)
 * docker-compose (tested on version 1.23.1)

### Install Docker ( step 1 )

In order to have installed the docker in your environment. 
You can follow the guide here https://docs.docker.com/get-docker/.

### Install docker-compose ( step 2 )

You need to install the docker-compose in your environment. 
You can follow the guide here https://docs.docker.com/compose/install/.

# Running Application

### Simple one-time run

You can start the build by running the docker compose file.

```
docker-compose up --build
```


### Running as a daemon on the background

If you want to run the application as a daemon on background, you can use this command to start application

```
docker-compose stop && docker-compose up --build -d
```

This command to access application logs

```
docker-compose logs -f
```

And this command to stop the application

```
docker-compose stop
```

### Accessing the system bash

If you want to install the new python package, freeze current packages etc etc, you need to access the internal bash of the docker. First, you need to have the application started as a deamon ( one step above ).

Then, please execute:

```
docker-compose exec server bash
```


Once you are you can simply install the python package as you are used to ( e.g. `pip install YOUR_PACKAGE` or `pip freeze -r requirements.txt` ).

