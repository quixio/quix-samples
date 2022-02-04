const https = require('https')

this.workspace = '{placeholder:broker.security.username}';
this.domain = '{placeholder:environment.subdomain}';
this.bearerToken = '{placeholder:token}';

let getGameResult = (streamId, callback) => {

    let url_host = `telemetry-query-${this.workspace}.${this.domain}.quix.ai`;
    let url_path = "/parameters/data";

    const options = {
        'method': 'POST',
        'hostname': url_host,
        'path': url_path,
        'headers': {
            'accept': 'text/plain',
            'Authorization': 'Bearer ' + this.bearerToken,
            'Content-Type': 'application/json'
        },
        'maxRedirects': 20
    };

    const req = https.request(options, function (res) {
        const chunks = [];

        res.on("data", function (chunk) {
            chunks.push(chunk);
        });

        res.on("end", function (chunk) {
            const body = Buffer.concat(chunks);
            const rtn = {
                dataPoints: JSON.parse(body.toString()).numericValues['count(Y_grav)']
            }
            callback(rtn);
        });

        res.on("error", function (error) {
            console.error(error);
        });
    });

    const postData = JSON.stringify({
        "numericParameters": [
            {
                "parameterName": "Y_grav",
                "aggregationType": "Count"
            }
        ],
        "stringParameters": [],
        "streamIds": [
            streamId
        ]
    });

    req.write(postData);
    req.end();
};

module.exports ={
    getGameResult: getGameResult
}
