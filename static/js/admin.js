function printChecklist() {
  let listDiv = document.getElementById("task-list");

  while (listDiv.lastChild) {
    listDiv.removeChild(listDiv.lastChild);
  }

  let totalTime = 1;
  let itemCount = checklist.length;

  checklist.forEach(function(item) {
    let date = new Date(item.projected_timestamp * 1000);
    let timeString = getUTCStringFromDate(date);

    let element = document.createElement('li');
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

window.setInterval(function() {
  loadChecklist('../tracker/');
  updateCurrentTime();
}, 1000);
