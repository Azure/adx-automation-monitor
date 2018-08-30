import React from 'react';

export default class RunSummaryView extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let query = "";
        if (run_data.query !== "") {
            query = <span className="badge badge-secondary mr-1">Query {run_data.query}</span>
        }

        return (
            <div className="container">
                <h1 className="display-1">Run <span className="display-4">{run_data.id}</span></h1>
                <h3>
                    <span className="badge badge-primary badge-pill mr-1">{run_data.remark}</span>
                    <span className="badge badge-danger badge-pill mr-1">Failure {run_data.failed_tasks_count}</span>
                    <span className="badge badge-info badge-pill mr-1">Total {run_data.total_tasks_count}</span>
                    <span className="badge badge-info badge-pill mr-1">{run_data.status}</span>
                </h3>
                <h5>
                    <span className="badge badge-secondary mr-1">{run_data.creation}</span>
                    <span className="badge badge-secondary mr-1">{run_data.image}</span>
                    {query}
                </h5>
            </div>
        )
    }
}