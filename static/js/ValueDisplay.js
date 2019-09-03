import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"

export class ValueDisplay extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: "&emdash;"
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

    render() {
        let valueHolder;

        if (this.props.unitSign) {
            valueHolder = <span className="value-holder">{ this.state.value } { this.props.unitSign }</span>;
        } else {
            valueHolder = <span className="value-holder">{ this.state.value }</span>;
        }

        return (
            <React.Fragment>
                <dt className="col-sm-3 value-label">{ this.props.label }</dt>
                <dd className="col-sm-9 value-display">
                    { valueHolder }
                </dd>
            </React.Fragment>
        );
    }
}

