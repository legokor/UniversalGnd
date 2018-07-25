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

function printLaunchList(launches) {
    console.log(launches);
    var taskSelector = document.getElementById('task-selector');
    if (launches.length === 0) {
        console.log("There are no available launches.");
        var noOption = document.createElement('option');
        noOption.appendChild(document.createTextNode('No launches available.'));
        noOption.disabled = true;
        noOption.selected = true;
        taskSelector.appendChild(noOption);
    } else {
        launches.forEach(function (launch) {
            var option = document.createElement('option');
            option.value = launch.id;
            option.appendChild(document.createTextNode(launch.name));
            if (launches.indexOf(launch) === launches.length - 1) {
                option.selected = true;
            }
            taskSelector.appendChild(option);
        });
    }
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
    } else if (data.type === 'update') {
        updateTask(data.data);
    } else {
        if ('lat' in data) {
            parseCoordinatesMessage(data);
        } else if ('timestamp' in data) {
            parseGenericMessage(data);
        } else if ('launches' in data) {
            printLaunchList(data.launches);
        }
    }
}
