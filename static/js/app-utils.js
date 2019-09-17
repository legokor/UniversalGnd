export function prettifyNumber(number) {
    return number < 10 ? "0" + number : number.toString();
}

export function getUTCStringFromDate(date) {
    let year = date.getUTCFullYear();
    let month = prettifyNumber(date.getUTCMonth() + 1);
    let day = prettifyNumber(date.getUTCDate());
    let hour = prettifyNumber(date.getUTCHours());
    let minute = prettifyNumber(date.getUTCMinutes());
    let second = prettifyNumber(date.getUTCSeconds());
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
}
