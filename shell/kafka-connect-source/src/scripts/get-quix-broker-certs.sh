#!/usr/bin/env bash

# Check if the environment variable is set

if [ -z "$Quix__Portal__Api" ]; then
    echo "Error: Environment variable Quix__Portal__Api is not set."
    exit 1
fi

if [ -z "$Quix__Workspace__Id" ]; then
    echo "Error: Environment variable Quix__Workspace__Id is not set."
    exit 1
fi

if [ -z "$Quix__Sdk__Token" ]; then
    echo "Error: Environment variable Quix__Sdk__Token is not set."
    exit 1
fi

if [ -z "$Quix__Deployment__Name" ]; then
    echo "Error: Environment variable Quix__Deployment__Name is not set."
    exit 1
fi

# Fetch the workspace details

workspaceDetails=$(curl -X 'GET' \
  "$Quix__Portal__Api/workspaces/$Quix__Workspace__Id" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $Quix__Sdk__Token")

brokerBootsrapList=$(echo "$workspaceDetails" | jq -r '.broker.address')
kafkaUsername=$(echo "$workspaceDetails" | jq -r '.broker.username')
kafkaPassword=$(echo "$workspaceDetails" | jq -r '.broker.password')
kafkaSecurityMode=$(echo "$workspaceDetails" | jq -r '.broker.securityMode')
kafkaSaslMechanism=$(echo "$workspaceDetails" | jq -r '.broker.saslMechanism')
sslPassword=$(echo "$workspaceDetails" | jq -r '.broker.sslPassword')

# Since KafkaSecurityMode has a different value in the portal and in the connect-distributed.properties file, we need to convert it

if [ "$kafkaSecurityMode" == "SaslSsl" ]; then
    kafkaSecurityMode="SASL_SSL"
elif [ "$kafkaSecurityMode" == "Ssl" ]; then
    kafkaSecurityMode="SSL"
elif [ "$kafkaSecurityMode" == "Sasl" ]; then
    kafkaSecurityMode="SASL_PLAINTEXT"
else 
    kafkaSecurityMode="PLAINTEXT"
fi

# Since KafkaSaslMechanism has a different value in the portal and in the connect-distributed.properties file, we need to convert it

if [ "$kafkaSaslMechanism" == "ScramSha256" ]; then
    kafkaSaslMechanism="SCRAM-SHA-256"
elif [ "$kafkaSaslMechanism" == "ScramSha512" ]; then
    kafkaSaslMechanism="SCRAM-SHA-512"
elif [ "$kafkaSaslMechanism" == "OAuthBearer" ]; then
    kafkaSaslMechanism="OAUTHBEARER"
elif [ "$kafkaSaslMechanism" == "Gssapi" ]; then
    kafkaSaslMechanism="GSSAPI"
else 
    kafkaSaslMechanism="PLAIN"
fi

export BOOTSTRAP_SERVERS=$brokerBootsrapList

# Fetch the broker certificates

curl -L "$Quix__Portal__Api/workspaces/$Quix__Workspace__Id/certificates" -H "Authorization: Bearer $Quix__Sdk__Token" -o /opt/certs.zip

mkdir -p /opt/quix
unzip -o /opt/certs.zip -d /opt/quix
rm -rf /opt/certs.zip

quixBrokerCertsPath="/opt/quix"
quixBrokerCertificateFile="$quixBrokerCertsPath/ca.cert"
quixBrokerTruststoreFile="$quixBrokerCertsPath/ca.jks"
quixBrokerTruststorePassword=$(cat /proc/sys/kernel/random/uuid)

# Create a truststore file based on the certificate file

keytool -importcert -file "$quixBrokerCertificateFile" -keystore "$quixBrokerTruststoreFile" -storepass "$quixBrokerTruststorePassword" -noprompt
