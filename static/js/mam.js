function mamParse(data) {
    for (var i = 1; i <= 4; ++i) {
        var btn = document.getElementById('switch-' + i);
        if (data['switch-' + i] === 0) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }
    for (var i = 1; i <= 2; ++i) {
        var btn = document.getElementById('button-' + i);
        if (data['button-' + i] === 0) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }

    var pot = document.getElementById('pot');
    pot.innerText = 'POT: ' + data['pot'];

    var mode = document.getElementById('mode');
    mode.innerText = 'MODE: ' + data['mode'];

    var fwd = document.getElementById('moving-forward');
    if (data['moving-forward']) {
        fwd.classList.add('active');
    } else {
        fwd.classList.remove('active');
    }

    var bwd = document.getElementById('moving-backward');
    if (data['moving-backward']) {
        bwd.classList.add('active');
    } else {
        bwd.classList.remove('active');
    }
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

var initButtonMam = document.getElementById('init-mam');
var comCookie = getCookie('com');
if (comCookie !== null) {
    var comInput = document.getElementById('com');
    comInput.value = comCookie;
}
initButtonMam.addEventListener('click', function (event) {
    var com = document.getElementById('com');
    setCookie('com', com.value, 30);
    socket.send(JSON.stringify({'action': 'init', 'target': 'mam', 'com': com.value}));
});
