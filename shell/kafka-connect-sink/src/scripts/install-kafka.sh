#!/usr/bin/env bash

path=/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

if [[ ! $(curl -sfI "${downloadUrl}") ]]; then
    downloadUrl="https://archive.apache.org/dist/${path}"
fi

wget "${downloadUrl}" -O "/tmp/kafka.tgz"

tar xfz /tmp/kafka.tgz -C /opt

rm /tmp/kafka.tgz

ln -s /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka