import React from 'react';

export default class QueryModal extends React.Component {
    render() {
        return (
            <div className="modal fade" id="queryModal" tabIndex="-1" role="dialog" aria-labelledby="exampleModalLabel"
                 aria-hidden="true">
                <div className="modal-dialog modal-dialog-centered" role="document">
                    <form action="{run_data.link}" method="get">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title" id="exampleModalLabel">Query tasks</h5>
                                <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div className="modal-body">
                                <div className="form-group">
                                    <input className="form-control" id="query" name="query" aria-describedby="queryHelp"
                                           placeholder="Enter query"/>
                                    <small id="queryHelp" className="form-text text-muted">
                                        {"The query string filters results base on tasks' identifiers."}
                                    </small>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                                <button type="submit" className="btn btn-primary">Query</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}