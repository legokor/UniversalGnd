let checklist = [];

function prettifyNumber(number) {
    return number < 10 ? "0" + number : number.toString();
}

function getUTCStringFromDate(date) {
    let year = date.getUTCFullYear();
    let month = prettifyNumber(date.getUTCMonth() + 1);
    let day = prettifyNumber(date.getUTCDate());
    let hour = prettifyNumber(date.getUTCHours());
    let minute = prettifyNumber(date.getUTCMinutes());
    let second = prettifyNumber(date.getUTCSeconds());
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
}

function updateCurrentTime() {
    let timeDiv = document.getElementById("current-time");
    timeDiv.innerHTML = getUTCStringFromDate(new Date());
}

function loadChecklist(checklistUrl = 'tracker/') {
    let notice = document.getElementById("notice");

    let request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState === XMLHttpRequest.DONE) {
            if (request.status === 200) {
                let response = JSON.parse(request.responseText);
                if (response.length === 0) {
                    notice.innerHTML = "Empty";
                    return;
                }
                if (request.responseText === JSON.stringify(checklist)) {
                    return;
                }
                checklist = [];
                response.forEach(function (item) {
                    checklist.push(item);
                });
                checklist.sort(function (a, b) {
                    if (a.projected_timestamp < b.projected_timestamp) return -1;
                    if (a.projected_timestamp > b.projected_timestamp) return 1;
                    return 0;
                });
                printChecklist();
            } else {
                notice.innerHTML = "Failed to load data, try refreshing";
            }
        }
    };

    request.open('GET', checklistUrl);
    request.send();
}

updateCurrentTime();
window.setInterval(function () {
    updateCurrentTime();
}, 1000);
