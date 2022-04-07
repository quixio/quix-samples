# Use Docker Locally

The docker file contained in this folder is how the docker image `quixpythonbaseimage` is built.
In order to use it locally, navigate to this folder in a terminal with Docker installed and execute the following command:
```
docker build . --tag quixpythonbaseimage
```
Once you did this, your project docker files should be able to build successfully when they reference `quixpythonbaseimage`.

# FAQ
1.
Q: Why is this not available as a public image?
A: The image will be made available at a later date through normal distribution channels, once we either managed to remove pythonnet dependency or managed to trim image size down.