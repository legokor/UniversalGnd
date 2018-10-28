function ConsoleMessage(msg) {
    this.container = document.createElement('p');
    this.container.className = 'console-msg';

    this.timeElem = document.createElement('span');
    this.timeElem.className = 'console-msg-time';
    this.timeElem.innerText = (new Date()).toLocaleTimeString();

    this.textElem = document.createElement('span');
    this.textElem.className = 'console-msg-text';
    this.textElem.innerText = msg;

    this.text = msg;

    this.container.appendChild(this.timeElem);
    this.container.appendChild(this.textElem);
}

function Console(containerDiv, sendFunc) {
    var outputContainer = containerDiv.getElementsByClassName('console-output')[0];
    var promptInput = containerDiv.getElementsByClassName('console-input')[0];
    var sendBtn = containerDiv.getElementsByClassName('console-send')[0];

    var messages = [];
    var localEcho = true;

    function recieveMessage(msgTxt) {
        let msg = new ConsoleMessage(msgTxt);
        messages.push(msg);
        outputContainer.appendChild(msg.container);
    };
    this.recieveMessage = recieveMessage;

    function sendMessage(msgTxt) {
        if (localEcho) recieveMessage(msgTxt);
        sendFunc(msgTxt);
    };
    this.sendMessage = sendMessage;

    sendBtn.onclick = function () {
        sendMessage(promptInput.value);
    }
}

let debugConsole = null;

window.addEventListener("load", function () {
    let dbgDiv = document.getElementById('debug-messages');

    if (dbgDiv != null) {
        debugConsole = new Console(
            dbgDiv,
            function (text) { socket.send(JSON.stringify({'action': 'send', 'data': text})); }
        );
    }
});

function displayMessage(data) {
    if (debugConsole === null) return;

    debugConsole.recieveMessage(data);
}

