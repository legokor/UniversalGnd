function printChecklist(checklist) {
    let listDiv = document.getElementById("task-list");

    while (listDiv.lastChild) {
        listDiv.removeChild(listDiv.lastChild);
    }

    checklist.forEach(function (item) {
        let date = new Date(item.projected_timestamp * 1000);
        let timeString = getUTCStringFromDate(date);

        let element = document.createElement('li');
        element.id = "task-" + item.id;
        let text = item.title + " (" + timeString + " UTC)";
        element.appendChild(document.createTextNode(text));

        let checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        if (item.actual_timestamp !== null) {
            checkbox.checked = 'checked';
        }
        checkbox.addEventListener('click', function () {
            let request = new XMLHttpRequest();
            request.open('POST', '../update-item/' + item.id);
            request.setRequestHeader('Content-Type', 'application/json');
            request.send(JSON.stringify({'value': parseFloat(document.getElementById('value-' + item.id).value), 'finished': checkbox.checked}));
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

        listDiv.appendChild(element);
    });
}

function messageParse(event) {
    let data = JSON.parse(event.data);
    if ('tasks' in data) {
        printChecklist(data.tasks);
    }
}
