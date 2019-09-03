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

function updateDestination(location) {
    destination = location;
    socket.send(JSON.stringify({'destination': {"longitude": location.lng(), "latitude": location.lat()}}));
}

function updateControlValue(name, value) {
    controlFields[name]["value"] = value;
    socket.send(JSON.stringify({'control': name, 'value': value}));
    let slider = document.getElementById(name);
    let text = document.getElementById(name + '-value');
    slider.value = value;
    text.value = value;
}


class EditableValueDisplay {

    constructor(cont, keyName, packetType, publishPacketType) {
        this.keyName = keyName;
        this.packetType = packetType;
        this.publishPacketType = publishPacketType;

        this.valueHolder = cont.getElementsByClassName('value-holder')[0];
        this.updateStatusHolder = cont.getElementsByClassName('update-status-holder')[0];

        this.valueHolder.addEventListener('keydown', (event) => {
            if (event.keyCode === 13) { // Enter
                this.publishValue();
            }
        });

        dispatcher.subscribe(packetType, (packet) => { this.updateValue(packet); });
    }

    updateValue(packet) {
        this.valueHolder.value = packet[this.keyName];
    }

    publishValue() {
        let packet = {};
        packet['type'] = this.publishPacketType;
        packet[this.keyName] = this.valueHolder.value;

        console.log(JSON.stringify(packet));
        socket.send(JSON.stringify(packet));

        if (this.updateStatusHolder != null) {
            this.updateStatusHolder.classList.add('saving');
            this.updateStatusHolder.classList.remove('saved');

            window.setTimeout(2500, () => {
                this.updateStatusHolder.classList.add('saved');
                this.updateStatusHolder.classList.remove('saving');
            });
        }
    }
}

let editableValueDisplays = [];

document.addEventListener("keydown", function (event) {
    event = event || window.event;

    // Hook up QC controls
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

window.addEventListener("load", function () {
    for (let field in controlFields) {
        let input = document.getElementById(field);
        if (input != null) {
            let text = document.getElementById(field + '-value');
            text.value = input.value;
            input.addEventListener('input', function () {
                let value = this.value;
                // updateControlValue(field, value);
            }, input);
        }
    }

    // Hook up EditableValueDisplays
    let editableValConts = document.getElementsByClassName('value-display-editable');
    for (let i = 0; i < editableValConts.length;  i++) {
        if (editableValConts[i].hasAttribute('data-packet-type') && editableValConts[i].hasAttribute('data-publish-packet-type')) {
            let packetType = editableValConts[i].getAttribute('data-packet-type');
            let publishPacketType = editableValConts[i].getAttribute('data-publish-packet-type');

            let keyName = 'value';
            if (editableValConts[i].hasAttribute('data-key-name')) {
                keyName = editableValConts[i].getAttribute('data-key-name');
            }

            editableValueDisplays.push(new EditableValueDisplay(editableValConts[i], keyName, packetType, publishPacketType));
        }
    }
});
