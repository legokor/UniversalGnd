for (var i = 1; i <= 8; ++i) {
    var button = document.getElementById('button-' + i);
    (function (id) {
        button.addEventListener('click', function (event) {
            socket.send(JSON.stringify({'action': 'button-click', 'id': id}));
        });
    })(i);
}
