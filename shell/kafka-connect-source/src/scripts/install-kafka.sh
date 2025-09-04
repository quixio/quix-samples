#!/usr/bin/env bash

kafkaFile="kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"

# Try self-hosted URL first
selfHostedUrl="https://quixstorageaccount.blob.core.windows.net/public-hosted/${kafkaFile}"
archiveUrl="https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${kafkaFile}"

echo "Attempting to download Kafka from self-hosted location..."
if wget -q --spider "${selfHostedUrl}" 2>/dev/null; then
    echo "Downloading from self-hosted: ${selfHostedUrl}"
    wget "${selfHostedUrl}" -O "/tmp/kafka.tgz"
else
    echo "Self-hosted not available, downloading from Apache archive..."
    wget "${archiveUrl}" -O "/tmp/kafka.tgz"
fi

tar xfz /tmp/kafka.tgz -C /opt

rm /tmp/kafka.tgz

ln -s /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka