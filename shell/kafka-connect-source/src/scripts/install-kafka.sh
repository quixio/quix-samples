#!/usr/bin/env bash
set -euo pipefail

kafkaFile="kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"
selfHostedUrl="https://quixstorageaccount.blob.core.windows.net/public-hosted/${kafkaFile}"
archiveUrl="https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${kafkaFile}"

if ! curl --fail --show-error --silent --location "$selfHostedUrl" --output /tmp/kafka.tgz; then
    curl --fail --show-error --silent --location "$archiveUrl" --output /tmp/kafka.tgz
fi

# Apache's published SHA-512 for kafka_2.13-3.6.1.tgz.
echo "1f063cd67463dd3bb5a5e06e7a1c2278db84bfc836a634fac7c9a005de66a42ac00b32f5e9bbdd22086605f73659efd4ce5bd1185196b02a743be0898daac55d  /tmp/kafka.tgz" | sha512sum -c -
tar xfz /tmp/kafka.tgz -C /opt
rm /tmp/kafka.tgz
ln -s "/opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}" /opt/kafka
