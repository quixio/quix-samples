class quixStreamWrapper {

    bearerToken = '';
    topicId = '';
    writerBaseUrl = '';
    workspace = '';
    domain = "";

    constructor(topicId, workspace, domain, bearerToken) {
        this.topicId = topicId;
        this.workspace = workspace;
        this.domain = domain;
        this.bearerToken = bearerToken;

        this.writerBaseUrl = `https://writer-${this.workspace}.${this.domain}.quix.ai`;
    }

    createStream = async () => {

        let url = `${this.writerBaseUrl}/topics/${this.topicId}/streams`

        try {

            let streamIdPromise = await fetch(url, {
                method: "POST",
                body: '{}',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `bearer ${this.bearerToken}`
                },
            });

            return JSON.parse(await streamIdPromise.text())['streamId'];
        }
        catch(reason){
            console.log("An error occurred sending the request to Quix " + reason);
        }
    };

    //note streamId does not need to exist.
    //a new stream will be created by the api
    sendEvent = async (streamId, id, value) => {
        let url = `${this.writerBaseUrl}/topics/${this.topicId}/streams/${streamId}/events/data`

        let timestamp = Date.now() * 1000000;

        try{
            await fetch(url, {
                method: "POST",
                body: JSON.stringify([{
                    "timestamp": timestamp,
                    "id": id,
                    "value": value
                }]),
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `bearer ${this.bearerToken}`
                },
            });
        }
        catch(reason){
            console.log("An error occurred sending the request to Quix " + reason);
        }
    }

    //note streamId does not need to exist.
    //a new stream will be created by the api
    sendParameterValue = async (streamId, values, name) => {
        let url = `${this.writerBaseUrl}/topics/${this.topicId}/streams/${streamId}/parameters/data`

        let timestamp = Date.now() * 1000000;
        try {
            await fetch(url, {
                method: "POST",
                body: JSON.stringify({
                    "timestamps": [timestamp],
                    "numericValues": values,
                    "tagValues": {
                        "Player": [name]
                    }
                }),
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `bearer ${this.bearerToken}`
                },
            });
        }
        catch(reason){
            console.log("An error occurred sending the request to Quix " + reason)
        }
    }

    startReaderHub = async () => {
        let url = `https://reader-${workspace}.${domain}.quix.ai/hub`;
        return this.startHub(url);
    }

    startWriterHub = async () => {
        let url = `https://writer-${workspace}.${domain}.quix.ai/hub`;
        return this.startHub(url);
    }

    startHub = async (url) => {
        let connection = new signalR.HubConnectionBuilder()
            .withUrl(url, {accessTokenFactory: () => this.bearerToken})
            .build();

        async function start() {
            try {
                await connection.start();
                console.log("SignalR Connected to " + url);
            } catch (err) {
                console.log(err);
                //try again in 5 seconds
                setTimeout(start, 5000);
            }
        };

        await start();
        return connection;
    }
}
