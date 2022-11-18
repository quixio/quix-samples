// constants
let debug = false;

let workspace = '{placeholder:broker.security.username}';
let domain = '{placeholder:environment.subdomain}';
let bearerToken = '{placeholder:token}';

let gameDataTopicName = "gamedata";
let carGameInputTopic = "car-game-input";

let stream_id = "";
let playerMessage;
let infoText;

let canMove = true;
let trackWidth = 1280;
let trackHeight = 720;
let trackImage = new Image();

let players = {};

let playerStartX = 600;
let playerStartY = 600;

if (debug) {
    playerStartX = 190;
    playerStartY = 400;
}

let remainingTimeSpan;
let remainingTime = 60;

let gameDataTopicStreamsWrapper = new quixStreamWrapper(gameDataTopicName, workspace, domain, bearerToken);
let carGameInputTopicStreamsWrapper = new quixStreamWrapper(carGameInputTopic, workspace, domain, bearerToken);

let myGameArea = {
    canvas: document.createElement("canvas"),
    start: function () {
        this.canvas.width = trackWidth;
        this.canvas.height = trackHeight;
        this.context = this.canvas.getContext("2d");

        document.getElementById("canvasDiv").appendChild(this.canvas);

        setInterval(updateGameArea, 20);
    },
    clear: function () {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

function startGame() {
    playerMessage = new TextComponent();

    if (debug) {
        infoText = new TextComponent();
    }

    myGameArea.start();
    setTrack(0);
}

function drawBox(color, box) {
    myGameArea.context.beginPath();
    myGameArea.context.lineWidth = "2";
    myGameArea.context.strokeStyle = color;
    myGameArea.context.rect(box.x, box.y, box.width, box.height);
    myGameArea.context.stroke();
}

function debugInfo() {

    let centre = this.findCentre();
    let hitBox = {
        x: centre.x - 10,
        y: centre.y - 10,
        width: 20,
        height: 20
    }

    //get representative sample of pixels under vehicle
    let colorAtPosition = myGameArea.context.getImageData(hitBox.x, hitBox.y, hitBox.width, hitBox.height).data;

    let isOnGrass = false;
    for (let pos = 0; pos < colorAtPosition.length; pos += 4) {
        if (colorAtPosition[pos] === 44) {
            isOnGrass = true;
            break;
        }
    }

    if (debug) {
        //draw hitBox
        drawBox("blue", hitBox);
        // draw cross hairs on car pivot point
        drawBox("red", {x: centre.x - 50, y: centre.y, width: 100, height: 1});
        drawBox("red", {x: centre.x, y: centre.y - 50, width: 1, height: 100});

        infoText.x = this.x;
        infoText.y = this.y;
        infoText.text = "ON GRASS=" + isOnGrass + "  cx=" + centre.x.toFixed(2) + ": cy=" + centre.y.toFixed(2) + " speed: " + this.speed.toFixed(2);
    }
}

function TextComponent(x, y, width, color, font) {

    this.text = "";
    this.width = width;
    this.font = font ?? "Ariel";
    this.x = x;
    this.y = y;

    this.update = function () {
        let ctx = myGameArea.context;

        ctx.save();

        ctx.font = this.width + " " + this.font;
        ctx.fillStyle = color;
        ctx.fillText(this.text, this.x, this.y);
    }
}

function CarComponent(width, height, color, x, y, type, id) {
    this.id = id;
    this.image = new Image();
    this.image.src = 'images/' + color;
    this.width = width;
    this.height = height;
    this.speed = 0;
    this.angle = 0;
    this.moveAngle = 0;
    this.x = x;
    this.y = y;

    this.findCentre = function () {
        return {
            x: this.x + (this.width / 2),
            y: this.y + (this.height / 2) - 10
        }
    }

    this.update = function () {
        let ctx = myGameArea.context;

        ctx.save();

        let carCentre = this.findCentre();
        ctx.translate(carCentre.x, carCentre.y);
        ctx.rotate(this.angle);
        ctx.translate(-carCentre.x, -carCentre.y);

        ctx.drawImage(this.image, this.x, this.y, this.width, this.height);

        //update the player info
        let playerInfoBox = document.getElementById(this.id);
        if (playerInfoBox) {
            playerInfoBox.innerHTML = getPlayerInfo(this);
        }

        ctx.restore();
    }
    this.newPos = function () {
        //if game hasn't started yet, prevent movement
        if (!canMove) return;

        debugInfo.call(this);
    }
}

function updateGameArea() {
    myGameArea.clear();

    myGameArea.context.drawImage(trackImage, 0, 0, trackWidth, trackHeight);

    for (let p in players) {
        players[p].newPos();
        players[p].update();
    }

    playerMessage.update();

    if (debug) {
        infoText.update();
    }
}

function addPlayer(playerName) {

    players[playerName] = new CarComponent(30, 60, "blue-car-t.png", playerStartX, playerStartY, "image");

    players[playerName].angle = -1.555;

    let playerInfoBoxId = createPlayerInfoBox()

    players[playerName].name = playerName;
    players[playerName].id = playerInfoBoxId;

    infoText = new TextComponent(players[playerName].x, players[playerName].y);
    infoText.text = "Car Info";
}

//connect to stream with signalr
async function connectToQuix() {

    await carGameInputTopicStreamsWrapper.startReaderHub().then(phoneConnection => {
        phoneConnection.invoke("SubscribeToParameter", "gamedata", stream_id, "Y_grav");
        phoneConnection.invoke("SubscribeToParameter", "gamedata", stream_id, "throttle");
        phoneConnection.invoke("SubscribeToParameter", "gamedata", stream_id, "brake");

        let phoneImage = document.getElementById("phoneImage");

        phoneConnection.on("ParameterDataReceived", data => {

            let angle = data.numericValues["Y_grav"][0];
            let braking = data.numericValues["brake"][0];
            let throttle = data.numericValues["throttle"][0];

            phoneImage.style.transform = "rotate(" + angle * 8 + "deg)"
            if (braking)
                phoneImage.src = "images/phone/-.png";
            else if (throttle)
                phoneImage.src = "images/phone/+.png";
            else if (throttle && braking)
                phoneImage.src = "images/phone/+-.png";
            else
                phoneImage.src = "images/phone/Default.png";
        });
    });

    await gameDataTopicStreamsWrapper.startReaderHub().then(connection => {
        connection.invoke("SubscribeToParameter", "car-game-control", stream_id + "-car-game-input-control", "x");
        connection.invoke("SubscribeToParameter", "car-game-control", stream_id + "-car-game-input-control", "y");
        connection.invoke("SubscribeToParameter", "car-game-control", stream_id + "-car-game-input-control", "angle");
        connection.invoke("SubscribeToParameter", "car-game-control", stream_id + "-car-game-input-control", "speed");

        let last_timestamp = 0;

        connection.on("ParameterDataReceived", data => {

            if (data.streamId.endsWith("-car-game-input-control")) {

                for (let p = 0; p < data.timestamps.length; p++) {

                    if (last_timestamp > 0 && last_timestamp - data.timestamps[p] > 0) {
                        console.log(last_timestamp - data.timestamps[p])
                    }

                    last_timestamp = data.timestamps[p];

                    let timestampms = (last_timestamp / 1000000)
                    let now = Date.now();

                    let x = data.numericValues.x[p];

                    let y = data.numericValues.y[p];
                    let speed = data.numericValues.speed[p];

                    let angle = data.numericValues.angle[p];

                    let playerName = data.tagValues.Player[p];

                    if (!players[playerName]) {
                        addPlayer(playerName);
                    }
                    if (players[playerName]) {
                        let player = players[playerName];

                        player.speed = speed;
                        player.angle = angle;

                        player.x = x;
                        player.y = y;
                        player.lastSync = now;
                    }
                }
            }
        });
    });
}

function init() {
    const urlParams = new URLSearchParams(window.location.search);
    stream_id = urlParams.get('streamid');
    if (stream_id !== null && stream_id !== undefined) {
        connectToQuix();

        remainingTimeSpan = document.getElementById("remainingTime");
        setInterval(() => {
            if (remainingTime <= 0) {
                window.location.href = "https://quix.io/data-stream-processing-example-results?streamId=" + stream_id;
            }
            remainingTimeSpan.innerText = remainingTime;
            remainingTime -= 1;
        }, 1000)

    }
}

function createPlayerInfoBox() {
    let id = uuidv4();
    let html = "<div id='" + id + "' style=\"margin: 1px; \" class=\"col-s-2\"></div>"
    document.getElementById("playersInfo").innerHTML += html;
    return id;
}

function getPlayerInfo(gameObject) {
    return "<div  style='min-width: 300px'>\n" +
        "       <div >\n" +
        "           Name: " + gameObject.name +
        "       </div>\n" +
        "       <div >\n" +
        "           Speed: " + gameObject.speed.toFixed(4) +
        "       </div>\n" +
        "   </div>\n";
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function setTrack(trackNumber) {

    let track = "track1.png";

    switch (trackNumber) {
        case 0:
            track = "track1.png";
            break;
        case 1:
            track = "track2.png";
            break;
        case 2:
            track = "track3.png";
            break;
    }

    trackImage.src = "images/" + track;
    carGameInputTopicStreamsWrapper.sendEvent(stream_id + "-car-game-input", "track", track);
}

startGame();
init();
