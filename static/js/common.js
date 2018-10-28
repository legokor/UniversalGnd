let socket = null;

function prettifyNumber(number) {
    return number < 10 ? "0" + number : number.toString();
}

function getUTCStringFromDate(date) {
    let year = date.getUTCFullYear();
    let month = prettifyNumber(date.getUTCMonth() + 1);
    let day = prettifyNumber(date.getUTCDate());
    let hour = prettifyNumber(date.getUTCHours());
    let minute = prettifyNumber(date.getUTCMinutes());
    let second = prettifyNumber(date.getUTCSeconds());
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
}

function updateCurrentTime() {
    let timeDiv = document.getElementById("current-time");
    timeDiv.innerText = getUTCStringFromDate(new Date());
}

function updateTask(data) {
    let taskDiv = document.getElementById("task-" + data.id);
    taskDiv.innerHTML = printItem(data).innerHTML;
    if (data.actual_timestamp !== null) {
        taskDiv.classList.add('completed');
    } else {
        taskDiv.classList.remove('completed');
    }
}

// Dispatches messages based on their 'type' attribute,
// by calling the registered callbacks of that type
function MessageDispatcher(webSocketUrl, openFunc) {

    this.msgCallbacks = {};

    this.registerMsgCallback = (type, func) => {
        if (!(type in this.msgCallbacks)) {
            this.msgCallbacks[type] = [];
        }
        this.msgtypes[type].append(func);
    }

    function dispatchMessage(msgTxt) {
        console.log(msgTxt);
        let msg = JSON.parse(msgTxt);

        displayMessage(msgTxt);

        // Fall back to the old messageParse function
        // if we don't know the type or there is none
        if (!('type' in msg) || this.msgCallbacks === undefined || !(msg['type'] in this.msgCallbacks) ) {
            messageParse(msg);
            return;
        }

        for (let type in Object.keys(this.msgCallbacks)) {
            if (msg.type == type) {
                for (let callback in this.msgCallbacks[type]) {
                    callback(msg);
                }
            }
        }
    }

    this.webSocket = new WebSocket("ws://" + webSocketUrl);
    this.webSocket.onopen = function (event) {
        openFunc();
    };
    this.webSocket.onmessage = function (event) {
        dispatchMessage(event.data);
    };
    this.webSocket.onerror = function() {
        alert('error!');
    };
    this.webSocket.onclose = function () {
        alert('Connection to the server was lost, refresh to reconnect!');
    };
}

function getLaunches() {
    socket.send(JSON.stringify({'action': 'get-launches'}));
}

function loadChecklist(checklistId) {
    socket.send(JSON.stringify({'action': "fetch", 'id': checklistId}))
}

let dispatcher = new MessageDispatcher(window.location.host + "/ws", getLaunches);
socket = dispatcher.webSocket;

updateCurrentTime();
window.setInterval(function () {
    updateCurrentTime();
}, 1000);
