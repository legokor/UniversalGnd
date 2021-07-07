import React from "react"

import { missionControlConnection as mcsc } from "./mcs-connection"

export class TaskList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const tasklist = this.props.tasklist;

        return (
            <ul className="task-list">
                { tasklist.map((group) => <TaskGroupItem key={group.id} group={group}>); }
            </ul>
        );
    }
}

