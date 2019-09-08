import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"
import { ConsoleMessage } from "./ConsoleMessage"

export class Console extends React.Component {
    constructor(props) {
        super(props);

        this.receiveMessage = this.receiveMessage.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
    }

    receiveMessage(msg) {
        this.setState((prevState) => ({
            messages: [...prevState.messages, msg]
        }));
    }

    sendMessage() {
        if (this.props.localEcho) {
            this.receiveMessage(msg)
        }

        mcsc.sendData({
            type: this.props.publishPacketType,
            [this.props.keyName]: this.state.value
        });
    }

    componentDidMount() {
        mcsc.subscribe(this.props.msgType, (msgdata) => {
            this.receiveMessage(msgdata[this.props.keyName]);
        });
    }

    componentWillUnmount() {

    }

    render() {
        const messages = this.state.messages.map((msg) => <ConsoleMessage value={msg}/>)

        return (
            <div className="console">
                <div class="console-output">{ messages }</div>
                { this.props.publishPacketType && <ConsolePrompt sendFunc={this.sendMessage}/> }
            </div>
        );
    }
}
