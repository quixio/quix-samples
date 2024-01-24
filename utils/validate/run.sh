docker build -t validate-quix-samples .
docker run -v "$(pwd)/../..:/data" validate-quix-samples
