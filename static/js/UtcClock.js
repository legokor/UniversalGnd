import React from 'react'

function prettifyNumber(number) {
    return number < 10 ? "0" + number : number.toString();
}

function toUTCTimeString(date) {
    let year = date.getUTCFullYear();
    let month = prettifyNumber(date.getUTCMonth() + 1);
    let day = prettifyNumber(date.getUTCDate());
    let hour = prettifyNumber(date.getUTCHours());
    let minute = prettifyNumber(date.getUTCMinutes());
    let second = prettifyNumber(date.getUTCSeconds());
    return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
}

export class UtcClock extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            date: new Date()
        };
    }

    tick() {
        this.setState({
            date: new Date()
        });
    }

    componentDidMount() {
        this.timerID = window.setInterval(
            () => this.tick(),
            500
        );
    }

    componentWillUnmount() {
        window.clearInterval(this.timerID);
    }

    render() {
        return (
            <p className="utc-clock">The current time is { toUTCTimeString(this.state.date) } UTC</p>
        );
    }

}
