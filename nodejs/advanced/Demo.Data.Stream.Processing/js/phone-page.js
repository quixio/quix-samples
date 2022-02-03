let workspace = '{placeholder:broker.security.username}';
let domain = '{placeholder:environment.subdomain}';
let bearerToken = '{placeholder:token}';
let gameDataTopicName = "gamedata";

let playerName = "Player1";
let forwardPressed = 0;
let brakePressed = 0;

const urlParams = new URLSearchParams(window.location.search);
const streamId = urlParams.get('streamid');

let streamWrapper = new quixStreamWrapper(gameDataTopicName, workspace, domain, bearerToken);
connection = null;

function joinGame() {
    streamWrapper.startWriterHub().then(connection => {
        this.connection = connection;

        doVibrate();
        console.log("SignalR connected.");

        let eventData = [
            {
                "timestamp": Date.now() * 1000000, // set now in nanoseconds,
                "id": "PlayerJoinedGame",
                "value": playerName
            }
        ]
        this.connection.invoke("SendEventData", gameDataTopicName, streamId, eventData);
    });

    //show / hide relevant controls
    document.getElementById("game-controls").hidden = false;
    document.getElementById("playerInfo").hidden = true;

    // feature detect
    if (typeof DeviceMotionEvent.requestPermission === 'function') {
        DeviceMotionEvent.requestPermission()
            .then(permissionState => {
                if (permissionState === 'granted') {
                    window.addEventListener('devicemotion', motion);
                }
            })
            .catch(e => {
                console.error(e);
            });
    } else {
        // handle regular non iOS 13+ devices
        window.addEventListener("devicemotion", motion, false);
    }
}

function doVibrate() {
    try {
        if (Notification.permission === "granted") {
            window.navigator.vibrate(150);
            window.navigator.vibrate(150);
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    window.navigator.vibrate(150);
                    window.navigator.vibrate(150);
                    window.navigator.vibrate(150);
                }
            });
        }
    } catch (err) {
        console.log("Error doing vibrate " + err)
    }
}

let lastSend = Date.now();

function motion(event) {

    //limit to 50hz
    let delta = Date.now() - lastSend;
    if ((delta) < 20) {
        return;
    }

    lastSend = Date.now();
    let timestamp = Date.now() * 1000000;

    let payload =
        {
            "timestamps": [timestamp],
            "numericValues": {
                "Y_grav": [event.accelerationIncludingGravity.y],
                "throttle": [forwardPressed],
                "brake": [brakePressed]
            },
            "tagValues": {
                "Player": [playerName]
            }
        }

    if (this.connection) {
        this.connection.invoke("SendParameterData", gameDataTopicName, streamId, payload);
        console.log("Sent payload")
    } else {
        console.log("No connection to Quix")
    }
}

//detect if browser supports motion events
if (window.DeviceMotionEvent) {
} else {
    console.log("DeviceMotionEvent is not supported");
    alert("Sorry your device is not supported")
}

//handle button presses
let brakeButton = document.getElementById("brakeButton");
let accelerateButton = document.getElementById("accelerateButton");

brakeButton.onpointerdown = function () {
    brakePressed = 1;
}
brakeButton.onpointerup = function () {
    brakePressed = 0;
}
brakeButton.ontouchend = function () {
    brakePressed = 0;
}

accelerateButton.onpointerdown = function () {
    forwardPressed = 1;
}
accelerateButton.onpointerup = function () {
    forwardPressed = 0;
}
accelerateButton.ontouchend = function () {
    forwardPressed = 0;
}

// function isLandscape() {
//     return window.innerWidth > window.innerHeight;
// }


// let ua = navigator.userAgent.toLowerCase();
// if (ua.indexOf('safari') != -1) {
//     if (ua.indexOf('chrome') > -1) {
//         // Chrome
//         screen.orientation.onchange = function (e) {
//             var orientation = (screen.orientation || {}).type || screen.mozOrientation || screen.msOrientation;
//
//
//         }
//     } else {
//         // Safari
//         window.addEventListener("orientationchange", function () {
//             // Announce the new orientation number
//             alert(window.orientation);
//         }, false);
//     }
// }


// if (navigator.userAgent.indexOf("Chrome") !== -1){
//     //if chrome, use screen.orientation.onchange
//     screen.orientation.onchange = function(e) {
//         var orientation = (screen.orientation || {}).type || screen.mozOrientation || screen.msOrientation;
//
//     }
// } else {
//     //if not chrome, try orientationchange
//     window.addEventListener("orientationchange", function() {
//         // Announce the new orientation number
//         alert(window.orientation);
//     }, false);
// }
