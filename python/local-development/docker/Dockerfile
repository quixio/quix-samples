FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
# Copy files used later during install
COPY ./kafkadepinstaller.sh .
# Install python and some utilities
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y python3.8 python3.8-distutils && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
#install mono (for pythonnet)
    apt-get install -y gnupg ca-certificates && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF && \
    echo "deb https://download.mono-project.com/repo/ubuntu stable-focal/snapshots/6.10.0 main" | tee /etc/apt/sources.list.d/mono-official-stable.list && apt-get update && \
    apt-get install -y mono-devel && \
# Workaround an issue with certs due to mono BTLS
    sed -i 's#mozilla/DST_Root_CA_X3.crt#!mozilla/DST_Root_CA_X3.crt#' /etc/ca-certificates.conf && update-ca-certificates && \
# install additional pythonnet dependencies
    apt-get install -y clang curl python3-dev libglib2.0 build-essential && \
    python3 -m pip install pycparser && \
# install generic dependencies of SDK to reduce build times
    python3 -m pip install pandas==1.2.1 pythonnet==2.5.1 && \
# Install librdkafka dependencies for ubuntu 20.04
    apt-get install -y dos2unix && \
    dos2unix ./kafkadepinstaller.sh && \
    chmod +x ./kafkadepinstaller.sh && \
    . ./kafkadepinstaller.sh && \
    rm /kafkadepinstaller.sh