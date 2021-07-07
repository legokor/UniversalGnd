function updateTask(data) {
    let taskDiv = document.getElementById("task-" + data.id);
    taskDiv.innerHTML = printItem(data).innerHTML;
    if (data.actual_timestamp !== null) {
        taskDiv.classList.add('completed');
    } else {
        taskDiv.classList.remove('completed');
    }
}

function getLaunches() {
    socket.send(JSON.stringify({'action': 'get-launches'}));
}

function loadChecklist(checklistId) {
    socket.send(JSON.stringify({'action': "fetch", 'id': checklistId}))
}
