import React from "react"

export class ConsoleMessage extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <p className="console-msg">
                <span className="console-msg-time">{ (new Date()).toLocaleTimeString() }</span>
                <span className="console-msg-text">{ this.props.value }</span>
            </p>
        );
    }
}
