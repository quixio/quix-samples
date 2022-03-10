var signalR = require("@microsoft/signalr");

const options = {
    accessTokenFactory: () => 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9vd25lcl9pZCI6ImF1dGgwfDRlODM4NjhjLTc4NmQtNGQ2NS04Y2MyLTUwODRkNDU5ODcxMiIsImh0dHBzOi8vcXVpeC5haS90b2tlbl9pZCI6ImZjZDQ0OGQxLTBjZGUtNDhmMi04ZmFhLTc5OTI0MzQxZTk0ZiIsImh0dHBzOi8vcXVpeC5haS9leHAiOiIxNjU1NzYyNDAwIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmRldi5xdWl4LmFpLyIsInN1YiI6IlhPaHZ6ZGkzUktMMkRMWHFJSlNhNWlFUjQwcjh6aG01QGNsaWVudHMiLCJhdWQiOiJodHRwczovL3BvcnRhbC1hcGkuZGV2LnF1aXguYWkvIiwiaWF0IjoxNjI3Njc0NjI0LCJleHAiOjE2MzAyNjY2MjQsImF6cCI6IlhPaHZ6ZGkzUktMMkRMWHFJSlNhNWlFUjQwcjh6aG01IiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOltdfQ.KjXyIunNvvEvQSKyfBoahfduilBgazUxiQPGfJlCgV4_jg59-Ctm-sgdpLc1qL6uk-XryzvlmPVhddgj1ToV6ftPfK2C58Lje2pPTJZmMCC6P6pZs-DUNydwIB_A36SPdbpbrVqLEJNqV8F79UGDkiEEN9vWPQ_Y5_i0aROLrRSdpbH_-edCw8KA8_MI197Fd32LvEb7U85Qb6AvD0I611hM7m5KFYr2mSPARfGQHDT3-7ewb5nqGyxeRt8LF3X_lVSR6hg-nCRwrpmiUKjDIb7qPp8enIFibocDta_vhaCJL2R6WajwSFXyVRwk0nyRsNZDgrpKsQSG5fr8TBH1rw'
};



export const CreateConnection = (onData, topic) => {
    const connection = new signalR.HubConnectionBuilder()
        .withUrl("https://reader-quixdev-alescamera.dev.quix.ai/hub", options)
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
            // let model = JSON.parse(data);
            // console.log("Received data from stream: " + model.streamId);
//            console.log("Received data from stream: ", JSON.parse(data));

            onData({image: data.stringValues.image[0]});

            // Unsubscribe from stream.
            // connection.invoke("UnsubscribeFromParameter", "your-topic-name", "your-stream-id", "your-parameter-id");
        });
    });

    return () => {
        connection.stop();
    }
}

