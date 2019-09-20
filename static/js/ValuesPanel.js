import React from "react"

export class ValuesPanel extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="panel">
                <dl className="row">
                    { this.props.values.map((value) => <ValueDisplay {...value}>) }
                </dl>
            </div>
        );
    }
}
