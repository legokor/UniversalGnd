import { CLIENT_WS_URL } from "./app-constants"

// Controls the connection to the Mission Control Server and
// dispatches received messages based on their 'type' attribute,
// by calling the registered callbacks of that type
class MissionControlConnection {

    constructor(webSocketUrl) {
        this.msgCallbacks = {};

        this.webSocket = new WebSocket(webSocketUrl);
        this.webSocket.onopen = (event) => {
            this.onMcsConnectionEstablished();
        };
        this.webSocket.onmessage = (event) => {
            this.dispatchMessage(event.data);
        };
        this.webSocket.onerror = function() {
            alert('error!');
        };
        this.webSocket.onclose = function () {
            alert('Connection to the server was lost, refresh to reconnect!');
        };
    }

    onMcsConnectionEstablished() {
        this.sendData({
            "action": "fetch-launch",
            "id": gndContext.mission.id
        });
    }

    // Register a callback to be called for every
    // recieved message of the given type
    subscribe(type, func) {
        if (!(type in this.msgCallbacks)) {
            this.msgCallbacks[type] = [];
        }
        this.msgCallbacks[type].push(func);
    }

    // Dispatches incoming MCS messages to subscribing functions based on type
    dispatchMessage(msgTxt) {
        let msg = JSON.parse(msgTxt);
        console.log(msg);

        Object.keys(this.msgCallbacks).forEach((type) => {
            if (msg.type.startsWith(type)) {
                this.msgCallbacks[type].forEach( (callback) => {
                    callback(msg);
                });
            }
        });
    }

    // Send JSON data to the Mission Control Server
    sendData(jsonData) {
        this.webSocket.send(JSON.stringify(jsonData));
    }

}

export const gndContext = JSON.parse(document.getElementById('gnd-context').textContent);
export const missionControlConnection = new MissionControlConnection(CLIENT_WS_URL);
