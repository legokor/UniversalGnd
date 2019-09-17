import React from 'react'

import { getUTCStringFromDate } from "./app-utils"

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
            <p className="utc-clock">The current time is { getUTCStringFromDate(this.state.date) } UTC</p>
        );
    }

}
