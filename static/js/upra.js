var initButtonUpra = document.getElementById('init-upra');
initButtonUpra.addEventListener('click', function (event) {
    var com = document.getElementById('com');
    socket.send(JSON.stringify({'action': 'init', 'target': 'upra', 'com': com.value}));
});

var programNameSubmit = document.getElementById('program-name-submit');
programNameSubmit.addEventListener('click', function (event) {
    socket.send(JSON.stringify({'action': 'program-name', 'data': document.getElementById('program-name').value}));
});

var programCommandSend = document.getElementById('program-command-send');
programCommandSend.addEventListener('click', function (event) {
    socket.send(JSON.stringify({'action': 'program-command', 'data': document.getElementById('program-command').value}));
});

var taskSelectSend = document.getElementById('task-selector-submit');
taskSelectSend.addEventListener('click', function (event) {
    var select = document.getElementById('task-selector');
    socket.send(JSON.stringify({'action': 'fetch-launch', 'id': select.options[select.selectedIndex].value}));
});

function upraParse(data) {
    if ('command-output' in data) {
        console.log(data);
        return;
    }
    console.log(data.latitude);
    console.log(data.longitude);
    var latitude = data.latitude;
    var latsign = latitude.substring(0, 2);
    var latdeg = parseInt(latitude.substring(1, 3));
    var latmin = parseFloat(latitude.substring(3));
    var lat = latdeg + latmin / 60;
    console.log(latdeg, latmin, lat);
    var longitude = data.longitude;
    var longsign = longitude.substring(0, 2);
    var longdeg = parseInt(longitude.substring(1, 4));
    var longmin = parseFloat(longitude.substring(4));
    var long = longdeg + longmin / 60;
    console.log(longdeg, longmin, long);
    parseCoordinatesMessage({'lat': lat, 'lng': long});
    parseGenericMessage({'altitude': data.altitude, 'timestamp': data.hours * 60 * 60 + data.minutes * 60 + data.seconds});
    parseGenericMessage({'exttemp': data.externaltemp, 'timestamp': data.hours * 60 * 60 + data.minutes * 60 + data.seconds});
}
