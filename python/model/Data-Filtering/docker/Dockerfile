FROM ubuntu:20.04
ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
# Install python and some utilities
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl python3.8 python3.8-distutils && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
#install mono (for pythonnet)
    DEBIAN_FRONTEND=noninteractive apt-get install -y gnupg ca-certificates && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF && \
    echo "deb https://download.mono-project.com/repo/ubuntu stable-focal/snapshots/6.10.0 main" | tee /etc/apt/sources.list.d/mono-official-stable.list && apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y mono-devel && \
# install additional pythonnet dependencies
    DEBIAN_FRONTEND=noninteractive apt-get install -y clang curl dos2unix python3-dev libglib2.0 build-essential && \
    python3 -m pip install pycparser && \
# install generic dependencies of SDK to reduce build times
    python3 -m pip install pandas==1.2.1 pythonnet==2.5.1
# Install librdkafka dependencies for ubuntu 20.04
COPY ./source/docker/kafkadepinstaller.sh .
RUN dos2unix ./kafkadepinstaller.sh && chmod +x ./kafkadepinstaller.sh && \
    /bin/bash ./kafkadepinstaller.sh && \
    rm /kafkadepinstaller.sh

RUN mkdir /app
WORKDIR /app
COPY ./source/requirements.txt ./source/requirements.txt
WORKDIR /app/source

RUN pip3 install -r ./requirements.txt --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/

ENTRYPOINT ["python3", "./main.py"]
