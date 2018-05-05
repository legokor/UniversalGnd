for (var i = 1; i <= 8; ++i) {
    var button = document.getElementById('button-' + i);
    (function (id) {
        button.addEventListener('click', function (event) {
            socket.send(JSON.stringify({'action': 'button-click', 'id': id}));
        });
    })(i);
}

var initButtonMam = document.getElementById('init-mam');
initButtonMam.addEventListener('click', function (event) {
    var com = document.getElementById('mam-com');
    socket.send(JSON.stringify({'action': 'init', 'target': 'mam', 'com': com.value}));
});
