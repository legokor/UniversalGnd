let destination = undefined;
let controlFields = {
    "roll": {
        "value": 0,
        "increaseKey": 68,
        "decreaseKey": 65,
    },
    "pitch": {
        "value": 0,
        "increaseKey": 87,
        "decreaseKey": 83,
    },
    "yaw": {
        "value": 0,
        "increaseKey": 39,
        "decreaseKey": 37,
    },
    "throttle": {
        "value": 0,
        "increaseKey": 38,
        "decreaseKey": 40,
    },
};

let charts = {};

function parseGenericMessage(data) {
    for (let key in data) {
        if (key in charts) {
            let chart = charts[key];
            if (chart.data.datasets[0].data.length > 10) {
                chart.data.datasets[0].data.shift();
            }
            chart.data.datasets[0].data.push({x: data["timestamp"], y: data[key]});
            chart.update(0);
        }
    }
}

function displayMessage(data) {
    document.getElementById('coordinates').innerHTML = data;
}

function updateDestination(location) {
    destination = location;
    socket.send(JSON.stringify({'destination': {"longitude": location.lng(), "latitude": location.lat()}}));
}

function sendMessage() {
    let input = document.getElementById('text');

    let text = input.value;
    input.value = '';
    socket.send(JSON.stringify({'action': 'send', 'data': text}));
}

function updateControlValue(name, value) {
    controlFields[name]["value"] = value;
    socket.send(JSON.stringify({'control': name, 'value': value}));
    let slider = document.getElementById(name);
    let text = document.getElementById(name + '-value');
    slider.value = value;
    text.value = value;
}

document.addEventListener("keydown", function (event) {
    event = event || window.event;

    for (let key in controlFields) {
        let value = controlFields[key]["value"];
        if (event.keyCode === controlFields[key]["increaseKey"]) {
            // updateControlValue(key, value + 1);
        }
        if (event.keyCode === controlFields[key]["decreaseKey"]) {
            // updateControlValue(key, value - 1);
        }
    }
});

window.onload = function () {
    let button = document.getElementById('send');
    button.addEventListener('click', function () {
        sendMessage();
    });

    for (let field in controlFields) {
        let input = document.getElementById(field);
        let text = document.getElementById(field + '-value');
        text.value = input.value;
        input.addEventListener('input', function () {
            let value = this.value;
            // updateControlValue(field, value);
        }, input);
    }
};
