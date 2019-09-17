import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"

export class TaskGroupItem extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const group = this.props.group;

        return (
            <li className="task-group-item">
                <span className="task-name">{ group.name }</span>
                <ul className="task-group-list">
                    { group.tasks.map((task) => <TaskItem key={task.id} task={task}>); }
                </ul>
            </li>
        );
    }
}

