$(date --date "1 second" +%s%9N)

date1=$(date +%s%9N)
date2=$(date --date "2 second" +%s%9N)
date3=$(date --date "4 second" +%s%9N)
date4=$(date --date "6 second" +%s%9N)

# Execute curl POST request to send data to the stream
curl -i -X POST "https://writer-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/topics/{placeholder:output}/streams/hello-world/parameters/data" \
-H "Authorization: bearer {placeholder:token}" \
-H "Content-Type: application/json" \
-d "{
    \"Timestamps\": [ $date1, $date2, $date3, $date4 ],
    \"NumericValues\": 
        {
            \"SomeParameter1\": [10.01, 202.02, 303.03, 250],
            \"SomeParameter2\": [400.04, 50.05, 60.06, 200]
        }
}"

# Execute curl POST request to close the stream
curl -i -X POST "https://writer-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai/topics/{placeholder:output}/streams/hello-world/close" \
-H "Authorization: bearer {placeholder:token}" \
-H "Content-Type: application/json"

# Explore data at https://portal.{placeholder:environment.subdomain}.quix.ai/data?workspace={placeholder:workspaceId}