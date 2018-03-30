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
            request.open('GET', '../toggle-item/' + item.id);
            request.send();
        });

        element.appendChild(checkbox);
        listDiv.appendChild(element);
    });
}

function displayMessage(a) {}
