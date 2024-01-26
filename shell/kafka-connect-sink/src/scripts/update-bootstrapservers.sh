#!/usr/bin/env bash

# Source the certificate and broker details script
source /usr/bin/get-quix-broker-certs.sh

echo "Bootstrap servers: $BOOTSTRAP_SERVERS"
echo "Kafka Username: $kafkaUsername"
echo "Kafka Password: ***"
echo "Kafka Security Mode: $kafkaSecurityMode"
echo "Kafka SASL Mechanism: $kafkaSaslMechanism"
echo "Quix Broker Truststore File: $quixBrokerTruststoreFile"
echo "Quix Broker Truststore Password: $quixBrokerTruststorePassword"

# Check if the environment variable is set
if [ -z "$BOOTSTRAP_SERVERS" ]; then
    echo "Error: Environment variable BOOTSTRAP_SERVERS is not set."
    exit 1
fi

if [ -z "$CONNECT_MODE" ] || [ "$CONNECT_MODE" == "standalone" ]; then
    file_path="/opt/kafka/config/connect-standalone.properties"
else
    file_path="/opt/kafka/config/connect-distributed.properties"
fi

new_bootstrap_servers="$BOOTSTRAP_SERVERS"

formatted_group_id=$(echo "${Quix__Workspace__Id}-${Quix__Deployment__Name}" | tr ' ' '-')

# Use sed to replace the bootstrap.servers value in the file
sed -i "s#<bootstrap_servers>#${new_bootstrap_servers}#g" "$file_path"
# Use sed to replace the group.id value in the file
sed -i "s#<group_id>#${formatted_group_id}#g" "$file_path"
# Use sed to replace kafka broker authentication values in the file
sed -i "s#<sasl_security_protocol>#${kafkaSecurityMode}#g" "$file_path"
sed -i "s#<sasl_mechanism>#${kafkaSaslMechanism}#g" "$file_path"
sed -i "s#<your_username>#${kafkaUsername}#g" "$file_path"
sed -i "s#<your_password>#${kafkaPassword}#g" "$file_path"
sed -i "s#<path_to_your_truststore>#${quixBrokerTruststoreFile}#g" "$file_path"
sed -i "s#<your_truststore_password>#${quixBrokerTruststorePassword}#g" "$file_path"

if [ "$CONNECT_MODE" == "distributed" ]; then

    kafkaOffsetStorageTopicName=${CONNECT_OFFSET_STORAGE_TOPIC:-"connect-offsets"}
    kafkaConfigConfigsTopicName=${CONNECT_CONFIG_STORAGE_TOPIC:-"connect-configs"}
    kafkaStatusStatusTopicName=${CONNECT_STATUS_STORAGE_TOPIC:-"connect-status"}
    kafkaOffsetStorageTopic="${Quix__Workspace__Id}-${kafkaOffsetStorageTopicName}"
    kafkaConfigStorageTopic="${Quix__Workspace__Id}-${kafkaConfigConfigsTopicName}"
    kafkaStatusStorageTopic="${Quix__Workspace__Id}-${kafkaStatusStatusTopicName}"

    create_topic() {
        local topic_name=$1
        curl -s -X POST \
            -H "Authorization: Bearer ${Quix__Sdk__Token}" \
            -H "Content-Type: application/json" \
            -d '{
                    "name": "'"${topic_name}"'",
                    "configuration": {
                    "partitions": 1,
                    "replicationFactor": 2,
                    "retentionInMinutes": 1440,
                    "retentionInBytes": 52428800,
                    "cleanupPolicy": "Compact"
                    }
                }' \
            "${Quix__Portal__Api}/${Quix__Workspace__Id}/topics" > /dev/null
    }

    get_topic_status() {
        local topic_name=$1
        result=$(curl -s -X GET \
            -H "Authorization: Bearer ${Quix__Sdk__Token}" \
            -H "Content-Type: application/json" \
            "${Quix__Portal__Api}/${Quix__Workspace__Id}/topics/${topic_name}")
        topicStatus=$(echo "$result" | jq -r '.status')
        echo "$topicStatus"
    }

    create_and_wait_for_topic() {
        local topic_name=$1
        local topic_display_name=$2

        # Check if the topic needs to be created
        topic_status=$(get_topic_status "$topic_name")
        echo "Topic status for $topic_display_name: $topic_status"

        if [ "$topic_status" != "Ready" ]; then
            echo "Topic $topic_display_name not found. Creating topic..."
            create_topic "$topic_name"

            # Wait for the topic to be created
            while [ "$(get_topic_status "$topic_name")" != "Ready" ]; do
                echo "Waiting for topic $topic_display_name to be created..."
                sleep 5
            done
        fi
        
    }

    create_and_wait_for_topic "$kafkaOffsetStorageTopicName" "$kafkaOffsetStorageTopic" &
    pid1=$!

    create_and_wait_for_topic "$kafkaConfigConfigsTopicName" "$kafkaConfigStorageTopic" &
    pid2=$!

    create_and_wait_for_topic "$kafkaStatusStatusTopicName" "$kafkaStatusStorageTopic" &
    pid3=$!

    if [ -n "$input" ]; then
        create_and_wait_for_topic "${input}" "${Quix__Workspace__Id}-${input}" &
    fi

    # Wait for all the topics to be created
    wait "$pid1" "$pid2" "$pid3"

    sed -i "s#^offset\.storage\.topic=.*#offset\.storage\.topic=${kafkaOffsetStorageTopic}#g" "$file_path"
    sed -i "s#^config\.storage\.topic=.*#config\.storage\.topic=${kafkaConfigStorageTopic}#g" "$file_path"
    sed -i "s#^status\.storage\.topic=.*#status\.storage\.topic=${kafkaStatusStorageTopic}#g" "$file_path"
fi


echo "Bootstrap servers updated ($BOOTSTRAP_SERVERS) successfully in $file_path"
