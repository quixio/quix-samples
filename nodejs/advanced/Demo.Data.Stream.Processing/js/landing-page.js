let workspace = '{placeholder:broker.security.username}';
let domain = '{placeholder:environment.subdomain}';
let bearerToken = '{placeholder:token}';
let gameDataTopicName = "{placeholder:gamedata}";

async function startNewGame() {
    let streamWrapper = new quixStreamWrapper(gameDataTopicName, workspace, domain, bearerToken);

    let stream_id = await streamWrapper.createStream();

    let host = window.location.host;
    let urlToPhonePage = `${window.location.protocol}//${host}/play?streamid=${stream_id}`
    let urlToTrackPage = `${window.location.protocol}//${host}/start?streamid=${stream_id}`

    let qrCodeObject = new QRCode(document.getElementById("qrcode"),
        {
            width: 230,
            height: 230
        }
    );

    qrCodeObject.makeCode(urlToPhonePage);

    document.getElementById("loading-spinner").style.visibility = "hidden";

    streamWrapper.startReaderHub().then(phoneConnection => {
        phoneConnection.invoke("SubscribeToEvent", gameDataTopicName, stream_id, "PlayerJoinedGame");

        // when player joins nav to game
        phoneConnection.on("EventDataReceived", data => {
            window.location.href = urlToTrackPage;
        });
    });
}

