function printItem(item, group = null) {
    let date = new Date(item.projected_timestamp * 1000);
    let timeString = getUTCStringFromDate(date);

    let element = document.createElement('div');
    element.id = "task-" + item.id;
    element.classList.add('progress');
    if (item.actual_timestamp !== null) {
        element.classList.add('completed');
    }
    let text = "";
    console.log(text, group);
    if (group !== null) {
        text += 'Group: ' + group + ', ';
    }
    console.log(text);
    text += item.title + " (" + timeString + " UTC)";
    if (item.has_value && item.value) {
        text += ', Value: ' + item.value;
    }
    element.appendChild(document.createTextNode(text));
    return element;
}

function printChecklist(checklist) {
    let listDiv = document.getElementById("task-matrix");
    while (listDiv.lastChild) {
        listDiv.removeChild(listDiv.lastChild);
    }

    checklist.forEach(function (item) {
        if ('orphaned' in item) {
            // tasks without a group
            console.log('orphaned tasks');
            item.tasks.forEach(function (task) {
                listDiv.appendChild(printItem(task));
            });
        } else {
            let group = item.name;
            console.log('Group: ' + group);
            item.tasks.forEach(function (task) {
                listDiv.appendChild(printItem(task, group));
            });
        }
    });
}

function messageParse(event) {
    console.log(event.data);
    displayMessage(event.data);
    let data = JSON.parse(event.data);
    if (data.type === 'upra') {
        upraParse(data.data);
    } else if (data.type === 'mam') {
        mamParse(data.data);
    } else if (data.type === 'checklist') {
        printChecklist(data.tasks);
    } else {
        if ('taskData' in data) {
            updateTask(data.taskData);
        } else if ('lat' in data) {
            parseCoordinatesMessage(data);
        } else if ('timestamp' in data) {
            parseGenericMessage(data);
        }
    }
}
