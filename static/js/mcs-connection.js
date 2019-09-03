import { AppConstants } from "./app-constants"

// Controls the connection to the Mission Control Server and
// dispatches received messages based on their 'type' attribute,
// by calling the registered callbacks of that type
class MissionControlConnection(webSocketUrl) {

    constructor() {
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

        displayMessage(msgTxt);

        // Fall back to the old messageParse function
        // if we don't know the type or there is none
        if (!('type' in msg) ||  !(msg['type'] in this.msgCallbacks) ) {
            messageParse(msg);
            return;
        }

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

export const missionControlConnection = new MissionControlConnection(AppConstants.CLIENT_WS_URL);
