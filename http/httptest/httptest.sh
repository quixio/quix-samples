# Execute curl POST request to send data to the stream
curl -X POST "https://writer-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/topics/{placeholder:outputTopicName}/streams/hello-world/parameters/data" \
-H "Authorization: bearer {placeholder:token}" \
-H "Content-Type: application/json" \
-d "{
    \"Timestamps\": [ 1591733989000000000, 1591733990000000000, 1591733991000000000, 1591733992000000000],
    \"NumericValues\": 
        {
            \"SomeParameter1\": [10.01, 202.02, 303.03, 250],
            \"SomeParameter2\": [400.04, 50.05, 60.06, 200]
        }
}"

# Execute curl POST request to close the stream
curl -i -X POST "https://writer-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/topics/{placeholder:outputTopicName}/streams/hello-world/close" \
-H "Authorization: bearer {placeholder:token}" \
-H "Content-Type: application/json"

# Explore data at https://portal.{placeholder:environment.subdomain}.quix.ai/data?workspace={placeholder:workspaceId}