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
    if (data.actual_timestamp !== null) {
        taskDiv.classList.add('completed');
    } else {
        taskDiv.classList.remove('completed');
    }
}

function initWebsocket(url) {
    socket = new WebSocket("ws://" + url);
    socket.onopen = function (event) {
        loadChecklist(1);
    };
    socket.onmessage = function (event) {
        displayMessage(event.data);
        let data = JSON.parse(event.data);
        if ('tasks' in data) {
            printChecklist(data.tasks);
        } else if ('taskData' in data) {
            updateTask(data.taskData);
        } else if ('lat' in data) {
            parseCoordinatesMessage(data);
        } else if ('timestamp' in data) {
            parseGenericMessage(data);
        }
    };
}

function loadChecklist(checklistId) {
    socket.send(JSON.stringify({'action': "fetch", 'id': checklistId}))
}

updateCurrentTime();
initWebsocket("localhost:8000/ws");
window.setInterval(function () {
    updateCurrentTime();
}, 1000);
