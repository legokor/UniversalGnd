import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"

export class TaskItem extends React.Component {
    constructor(props) {
        super(props);

        this.handleCheckChange = this.handleCheckChange.bind(this);
        this.handleValueChange = this.handleValueChange.bind(this);
    }

    componentDidMount() {
        mcsc.subscribe("task", (packet) => {
            this.setState({
                value: packet[this.props.keyName]
            });
        });
    }

    componentWillUnmount() {
    }

    handleValueChange(event) {
    }

    handleCheckChange(event) {
    }

    render() {
        const task = this.props.task;
        const taskComplete = item.actual_timestamp !== null;

        return (
            <li className={ "task-item" + (taskComplete ? " complete" : "") }>
                <label for={ "task-check-" + task.id } className="task-label">
                    <input type="check"
                        id={ "task-check-" + task.id }
                        checked={taskComplete} />;
                    <span className="task-name">{ task.name }</span>
                </label>
                { task.has_value &&
                    <div class="task-value-wrapper">
                        <span class="task-value-name">
                            { (task.value_name || "Value") + ":" }
                        </span>
                        <input type="number"
                            id={ "task-value-" + task.id }
                            onchange={ this.handleValueChange }/>
                    </div>
                }
            </li>
        );
    }
}

