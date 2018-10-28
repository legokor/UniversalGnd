String.prototype.format = function() {
    var args = arguments;

    return this.replace(/\{(\d+)\}/g, function() {
        return args[arguments[1]];
    });
};

function printItem(item, group = null) {
    let date = new Date(item.projected_timestamp * 1000);
    let timeString = getUTCStringFromDate(date);


    let wrapper_div = document.createElement('div');
    wrapper_div.className = 'input-group input-group-lg mb-3';
    let innerHTML_str = '\
    <div class="input-group-prepend">\
        <div class="input-group-text">\
            <input type="checkbox" class="" id="checkbox-{0}" {1}></input>\
        </div>\
    </div>\
    <label class="form-control input-group-text" for="checkbox-{0}">\
        <span>{2} ({3} UTC)</span>\
    </label>';
    wrapper_div.innerHTML = innerHTML_str.format(
        item.id, (item.actual_timestamp !== null ? ' checked="checked"' : ''),
        item.title, timeString);

    console.log(wrapper_div.innerHTML);

/*
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
*/
    var sendUpdate = function () {
        let request = new XMLHttpRequest();
        request.open('POST', '../update-item/' + item.id);
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            'value': document.getElementById('value-' + item.id) === null ? null : parseFloat(document.getElementById('value-' + item.id).value),
            'finished': checkbox.checked
        }));
    };

    let checkbox = wrapper_div.firstElementChild.firstElementChild.firstElementChild;
    checkbox.addEventListener('click', sendUpdate);
    //element.appendChild(checkbox);

    if (item.has_value) {
        let input = document.createElement('input');
        input.className = 'form-control';
        input.type = 'number';
        input.placeholder = 'Value';
        input.id = 'value-' + item.id;
        if (item.value) {
            input.value = item.value;
        }
        input.addEventListener('input', sendUpdate);
        //let input_append_wrapper = document.createElement('div');
        //input_append_wrapper.className = 'input-group-append';
        //input_append_wrapper.appendChild(input);
        wrapper_div.appendChild(input);
    }

    return wrapper_div;
}

function printLaunchList(launches) {
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

function printChecklist(checklist) {
    let listDiv = document.getElementById("task-list");
    while (listDiv.lastChild) {
        listDiv.removeChild(listDiv.lastChild);
    }

    checklist.forEach(function (item) {
        if ('orphaned' in item) {
            // tasks without a group
            item.tasks.forEach(function (task) {
                listDiv.appendChild(printItem(task));
            });
        } else {
            let group = item.name;
            item.tasks.forEach(function (task) {
                listDiv.appendChild(printItem(task, group));
            });
        }
    });
}

function messageParse(data) {
    if (data.type === 'checklist') {
        printChecklist(data.tasks);
    } else if ('launches' in data) {
        printLaunchList(data.launches);
    }
}

var taskSelectSend = document.getElementById('task-selector-submit');
taskSelectSend.addEventListener('click', function (event) {
    var select = document.getElementById('task-selector');
    socket.send(JSON.stringify({'action': 'fetch-launch', 'id': select.options[select.selectedIndex].value}));
});
