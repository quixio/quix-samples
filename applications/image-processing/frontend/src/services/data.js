var signalR = require("@microsoft/signalr");


export const CreateConnection = (onData, topic) => {
    let connection;
    let stopped = false;

    ( async () => {
        let workspace_id = await (fetch('/workspace_id').then((e)=>e.text()));
        let sdk_token = await (fetch('/sdk_token').then((e)=>e.text()));

        if(stopped){ return; }

        const options = {
            accessTokenFactory: () => sdk_token
        };

        connection = new signalR.HubConnectionBuilder()
        .withUrl(`https://reader-${workspace_id}.dev.quix.ai/hub`, options)
        .build();

        // Establish connection
        connection.start().then(() => {
            console.log("Connected to Quix.");

            // Subscribe to parameter data stream.
            ["image"].forEach((parameterid) => {
                connection.invoke("SubscribeToParameter", topic, "input-image", parameterid);
            });

            // Read data from the stream.
            connection.on("ParameterDataReceived", data => {
                onData({image: data.stringValues.image[0]});
            });
        });

    })();


    return () => {
        if(connection)
        {
            connection.stop();
        }
        stopped = true;
    }
}
