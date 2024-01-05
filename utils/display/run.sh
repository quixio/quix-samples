docker build -t display-quix-samples .
docker run -v "$(pwd)/../..:/data" display-quix-samples
