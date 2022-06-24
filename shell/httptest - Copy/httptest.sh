nanosecsinsecs=1000000000
date1=$(date +%s)
date2=$((($date1+2)*nanosecsinsecs))
date3=$((($date1+4)*nanosecsinsecs))
date4=$((($date1+6)*nanosecsinsecs))
date1=$((($date1)*nanosecsinsecs))

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