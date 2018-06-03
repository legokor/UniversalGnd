function printItem(item, group = null) {
    let date = new Date(item.projected_timestamp * 1000);
    let timeString = getUTCStringFromDate(date);

    let element = document.createElement('li');
    element.id = "task-" + item.id;
    let label = document.createElement('label');
    label.setAttribute('for', 'checkbox-' + item.id);
    let text = item.title + " (" + timeString + " UTC)";
    label.appendChild(document.createTextNode(text));
    element.appendChild(label);

    let checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = 'checkbox-' + item.id;
    if (item.actual_timestamp !== null) {
        checkbox.checked = 'checked';
    }
    checkbox.addEventListener('click', function () {
        let request = new XMLHttpRequest();
        request.open('POST', '../update-item/' + item.id);
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            'value': document.getElementById('value-' + item.id) === null ? null : parseFloat(document.getElementById('value-' + item.id).value),
            'finished': checkbox.checked
        }));
    });
    element.appendChild(checkbox);

    if (item.has_value) {
        let input = document.createElement('input');
        input.type = 'number';
        input.placeholder = 'Value';
        input.id = 'value-' + item.id;
        if (item.value) {
            input.value = item.value;
        }
        element.appendChild(input);
    }

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
    let data = JSON.parse(event.data);
    if ('tasks' in data) {
        printChecklist(data.tasks);
    }
}
