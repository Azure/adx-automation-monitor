import { Table } from 'reactstrap';
import TasksCollection from '../models/tasks-collection.js'
import TaskFilterBadge from './task-filter.jsx'
import { TaskCategoriesBadges, TaskCategoryResetBadge } from './task-category.jsx'

const identifier_style = {
    overflow: "hidden",
    whiteSpace: "nowrapw",
    textOverflow: "ellipsis",
    maxWidth: "40rem"
};

function TaskRow(props) {
    let duration = props.task.duration
    if (props.task.duration < 1000) {
        duration = "< 1s"
    } else {
        duration = Math.round(duration / 1000);
        let seconds = duration % 60;
        let minutes = Math.floor(duration / 60);

        if (minutes > 0) {
            duration = "" + minutes + " min " + seconds + " sec";
        } else {
            duration = "" + seconds + " sec";
        }
    }

    return (<tr>
        <td><a href={props.task.link}>{props.task.id}</a></td>
        <td>{props.task.category}</td>
        <td style={identifier_style}>{props.task.identifier}</td>
        <td>{props.task.result}</td>
        <td>{duration}</td>
    </tr>);
}

function TaskHeader(props) {
    return <thead>
        <tr>
            <th>ID</th>
            <th>Category</th>
            <th>Identifier</th>
            <th>Result</th>
            <th>Duration</th>
        </tr>
    </thead>;
}

function TaskTableBody(props) {
    let content = props.tasks.map(each => <TaskRow task={each} />);

    return <tbody style={{ fontSize: "small" }}>
        {content}
    </tbody>
}

export default class TasksView extends React.Component {
    constructor(props) {
        super(props);
        this._tasks = new TasksCollection(props.tasks, props.failed_only, props.category);
        this.state = {
            query: props.query,
            failed_only: props.failed_only,
            tasks: this._tasks.tasks,
            category: props.category,
            categories: this._tasks.categories,
        };
    }

    toggleFailedOnly() {
        let new_state = !this.state.failed_only;
        this._tasks.failed = new_state;

        this.setState({
            failed_only: new_state,
            tasks: this._tasks.tasks,
            categories: this._tasks.categories,
        });
    }

    toggleCategory(category) {
        if (this.state.category === category) {
            category = ""
        }

        this._tasks.category = category;

        this.setState({
            category: category,
            tasks: this._tasks.tasks,
            categories: this._tasks.categories
        });
    }

    renderControlPanel() {
        return <div className="row mb-4">
            <div className="col">
                <div className="container">
                    <TaskFilterBadge failed={this.state.failed_only} onClick={() => this.toggleFailedOnly()} />
                    <TaskCategoriesBadges categories={this.state.categories}
                        current_category={this.state.category}
                        onClick={(category) => this.toggleCategory(category)} />
                    <TaskCategoryResetBadge onClick={() => this.toggleCategory("")} />
                </div>
            </div>
        </div>;
    }

    renderTasksViewTable() {
        return <div className="row">
            <div className="col">
                <table className="table table-sm table-striped table-hover">
                    <TaskHeader />
                    <TaskTableBody tasks={this.state.tasks} />
                </table>
            </div>
        </div>
    }

    render() {
        return (
            <div>
                {this.renderControlPanel()}
                {this.renderTasksViewTable()}
            </div >
        );
    }
}