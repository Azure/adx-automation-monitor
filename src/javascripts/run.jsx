import React from 'react';
import ReactDOM from 'react-dom';
// import RunView from './components/run-view.jsx';
// import QueryModal from './components/tasks-query.jsx';

import Navbar from './components/navbar.jsx';
import GeneralHeader from './components/general-header.jsx';


// ReactDOM.render(<RunView tasks={tasks_data} failed_only={true} category=""/>, document.getElementById('tasks_view'));
// ReactDOM.render(<QueryModal/>, document.getElementById('query_modal'));

const mainBody = <div>
    <GeneralHeader />
</div>;

ReactDOM.render(<Navbar/>, document.getElementById('nav'));
ReactDOM.render(mainBody, document.getElementById('main'));
