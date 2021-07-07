import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"

export class EditableValueDisplay extends React.Component {
    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);

        this.state = {
            value: ""
        };
    }

    componentDidMount() {
        mcsc.subscribe(this.props.msgType, (packet) => {
            this.setState({
                value: packet[this.props.keyName]
            });
        });
    }

    componentWillUnmount() {
        // FIXME: Implement unsubscribe
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
    }

    handleSubmit(event) {
        event.preventDefault();

        mcsc.sendData({
            type: this.props.publishPacketType,
            [this.props.keyName]: this.state.value
        });
    }

    render() {
        let valueLabel;

        if (this.props.unitSign) {
            valueLabel = <dt className="col-sm-3 value-label">{ this.props.label } ({ this.props.unitSign })</dt>;
        } else {
            valueLabel = <dt className="col-sm-3 value-label">{ this.props.label }</dt>;
        }

        return (
            <React.Fragment>
                { valueLabel }
                <dd className="col-sm-9 value-display">
                    <form onSubmit={ this.handleSubmit }>
                        <input type={ this.props.valueType } />
                        <input type="submit" value="Set"/>
                    </form>
                </dd>
            </React.Fragment>
        );
    }
}

