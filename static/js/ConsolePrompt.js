import React from "react"

export class ConsolePrompt extends React.Component {
    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);

        this.state = {
            value: ""
        };
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
    }

    handleSubmit(event) {
        event.preventDefault();
        this.props.sendFunc(this.state.value);
    }

    render() {
        return (
            <form class="console-prompt input-group" onsubmit={ this.handleSubmit }>
                <input class="console-input form-control" placeholder={ this.props.txtPlaceholder } onchange={ this.handleChange } />
                <div class="input-group-append">
                    <input type="submit" class="console-send btn btn-dark" value={ this.props.} />
                </div>
            </form>
        );
    }
}


