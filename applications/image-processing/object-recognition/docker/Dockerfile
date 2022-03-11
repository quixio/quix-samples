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
COPY ./docker/kafkadepinstaller.sh .
RUN dos2unix ./kafkadepinstaller.sh && chmod +x ./kafkadepinstaller.sh && \
    /bin/bash ./kafkadepinstaller.sh && \
    rm /kafkadepinstaller.sh


RUN apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev \
  libavformat-dev libswscale-dev
RUN  apt-get update && apt-get install -y python3-dev python3-numpy \
  python3 python3-pip python3-dev libtbb2 libtbb-dev \
  libjpeg-dev libdc1394-22-dev \
  python3-opencv libopencv-dev python3-pycurl \
  libatlas-base-dev gfortran webp qt5-default libvtk6-dev zlib1g-dev

# RUN pip3 install numpy

# RUN apt-get install -y python-pip
# RUN pip install --upgrade pip

RUN cd ~/ &&\
    git clone https://github.com/Itseez/opencv.git &&\
    git clone https://github.com/Itseez/opencv_contrib.git &&\
    cd opencv && mkdir build && cd build && cmake  -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON .. && \
    make -j8 && make install && ldconfig && rm -rf ~/opencv*  # Remove the opencv folders to reduce image size

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
WORKDIR /app/source

RUN pip3 install -r ./requirements.txt  --extra-index-url https://pkgs.dev.azure.com/quix-analytics/53f7fe95-59fe-4307-b479-2473b96de6d1/_packaging/public/pypi/simple/

ENTRYPOINT ["python3", "./main.py"]
