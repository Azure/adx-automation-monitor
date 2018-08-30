import ReactDOM from 'react-dom';
import TasksView from './components/tasks-view.jsx';
import RunSummaryView from './components/run-summary-view.jsx';
import QueryModal from './components/tasks-query.jsx';



ReactDOM.render(<RunSummaryView/>, document.getElementById('run_summary'));
ReactDOM.render(<TasksView tasks={tasks_data} failed_only={true} category="" />, document.getElementById('tasks_view'));
ReactDOM.render(<QueryModal/>, document.getElementById('query_modal'));
