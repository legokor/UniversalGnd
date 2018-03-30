function printChecklist(checklist) {
    let listDiv = document.getElementById("task-matrix");

    while (listDiv.lastChild) {
        listDiv.removeChild(listDiv.lastChild);
    }

    checklist.forEach(function (item) {
        let date = new Date(item.projected_timestamp * 1000);
        let timeString = getUTCStringFromDate(date);

        let element = document.createElement('div');
        element.id = "task-" + item.id;
        element.classList.add('progress');
        if (item.actual_timestamp !== null) {
            element.classList.add('completed');
        }
        let text = item.title + " (" + timeString + " UTC)";
        element.appendChild(document.createTextNode(text));
        listDiv.appendChild(element);
    });
}
