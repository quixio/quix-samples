var https = require('https');

// Get bearer token from platform.
const token = "bearer {placeholder:token}";

// Set the Workspace and Topic
const workspaceId = "{placeholder:workspaceId}";
const topicName = "{placeholder:output}";
const streamId = "hello-world-stream";

current_date = new Date().getTime();
now_plus_2 = (current_date + 20000) * 1000 * 1000;
now_plus_4 = (current_date + 40000) * 1000 * 1000;
now_plus_6 = (current_date + 60000) * 1000 * 1000;


var data = JSON.stringify({
"Timestamps": [ now_plus_2, now_plus_4, now_plus_6 ],
"NumericValues":
    {
        "SomeParameter1": [10.01, 202.02, 303.03],
        "SomeParameter2": [400.04, 50.05, 60.06]
    }
});

var options = {
  host: `writer-${workspaceId}.dev.quix.ai`,
  port: '443',
  path: `/topics/${topicName}/streams/${streamId}/parameters/data`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': data.length,
    'Authorization': token
  }
};

var req = https.request(options, res => {
  var msg = '';
  res.on('data', chunk => msg += chunk);
  res.on('end', () => console.log("Response: " + res.statusCode));
});

req.write(data);
req.end();