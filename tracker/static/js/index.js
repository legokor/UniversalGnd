let socket = new WebSocket("ws://152.66.156.206:8000/");
let map = undefined;
let flightPath = undefined;
let coordinatesArray = [];
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

socket.onopen = function (event) {
    console.log("WebSocket.onopen");
};

function parseCoordinatesMessage(data) {
    // parse GPS message
    let coordinates = data;
    coordinatesArray.push(coordinates);
    if (flightPath === undefined) {
        let flightPath = new google.maps.Polyline({
            path: coordinatesArray,
            geodesic: true,
            strokeColor: '#0000FF',
            strokeOpacity: 0.5,
            strokeWeight: 5
        });
        flightPath.setMap(map);
    } else {
        flightPath.setPath(coordinatesArray);
    }

    map.panTo(coordinates);
}

function parseGenericMessage(data) {
    for (key in data) {
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

socket.onmessage = function (event) {
    let data = JSON.parse(event.data);

    displayMessage(event.data);

    if ('lat' in data) {
        parseCoordinatesMessage(data);
    } else if ('timestamp' in data) {
        parseGenericMessage(data);
    }
};

function initMap() {
    let coordinates = {lat: 47.4734, lng: 19.0598};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 20,
        center: coordinates,
        mapTypeId: 'hybrid',
    });
    map.setTilt(0);
    google.maps.event.addListener(map, 'click', function (event) {
        placeMarker(event.latLng);
    });
}

function updateDestination(location) {
    destination = location;
    socket.send(JSON.stringify({'destination': {"longitude": location.lng(), "latitude": location.lat()}}));
}

function placeMarker(location) {
    if (destination === undefined) {
        updateDestination(location);
        let marker = new google.maps.Marker({
            position: destination,
            map: map,
            draggable: true,
        });
        google.maps.event.addListener(marker, 'dragend', function () {
            updateDestination(marker.getPosition());
        });
        google.maps.event.addListener(marker, 'rightclick', function () {
            marker.setMap(null);
            destination = undefined;
        });
    }
}

function sendMessage() {
    let input = document.getElementById('text');

    let text = input.value;
    input.value = '';
    socket.send(JSON.stringify({'text': text}));
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
            updateControlValue(key, value + 1);
        }
        if (event.keyCode === controlFields[key]["decreaseKey"]) {
            updateControlValue(key, value - 1);
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
            let name = field;
            updateControlValue(name, value);
        }, input);
    }
};
