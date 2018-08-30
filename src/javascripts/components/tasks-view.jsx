import {Table} from 'reactstrap';
import TasksCollection from '../models/tasks-collection.js'
import TaskFilterBadge from './task-filter.jsx'
import {TaskCategoriesBadges, TaskCategoryResetBadge} from './task-category.jsx'


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

    render() {
        const identifier_style = {
            overflow: "hidden",
            whiteSpace: "nowrapw",
            textOverflow: "ellipsis",
            maxWidth: "40rem"
        };

        let content = this.state.tasks.map((each) => (
            <tr>
                <td><a href={each.link}>{each.id}</a></td>
                <td>{each.category}</td>
                <td style={identifier_style}>{each.identifier}</td>
                <td>{each.result}</td>
            </tr>));

        return (
            <div>
                <div className="row mb-4">
                    <div className="col">
                        <div className="container">
                            <TaskFilterBadge failed={this.state.failed_only} onClick={() => this.toggleFailedOnly()}/>
                            <TaskCategoriesBadges categories={this.state.categories}
                                                  current_category={this.state.category}
                                                  onClick={(category) => this.toggleCategory(category)} />
                            <TaskCategoryResetBadge onClick={() => this.toggleCategory("")}/>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col">
                        <Table size="sm" striped hover>
                            <thead>
                            <tr>
                                <th>ID</th>
                                <th>Category</th>
                                <th>Identifier</th>
                                <th>Result</th>
                            </tr>
                            </thead>
                            <tbody style={{fontSize: "small"}}>
                            {content}
                            </tbody>
                        </Table>
                    </div>
                </div>
            </div>
        )
    }
}