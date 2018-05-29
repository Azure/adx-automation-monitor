import json
from ._share import db


class Task(db.Model):
    # unique id
    id = db.Column(db.Integer, primary_key=True)
    # display name for the test task
    name = db.Column(db.String)
    # annotation of the task, used to fast query tasks under a run. its form is defined by the application.
    annotation = db.Column(db.String)
    # settings of the task. the settings can be saved in JSON or any other format defined by the application. settings
    # are immutable
    settings = db.Column(db.String)
    # status of the task: initialized, scheduled, completed, and ignored
    status = db.Column(db.String)
    # details of the task result. the value can be saved in JSON or any other format defined by the application. the
    # result details are mutable
    result_details = db.Column(db.String)
    # result of the test: passed, failed, and error
    result = db.Column(db.String)
    # the duration of the test run in milliseconds
    duration = db.Column(db.Integer)

    # relationship
    run_id = db.Column(db.Integer, db.ForeignKey('run.id'), nullable=False)
    run = db.relationship('Run', backref=db.backref('tasks', cascade='all, delete-orphan', lazy=True))

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._settings = None

    @property
    def identifier(self) -> str:
        return self.settings_in_json['classifier']['identifier']  # pylint: disable=unsubscriptable-object

    @property
    def log_path(self) -> str:
        return self.result_in_json['a01.reserved.tasklogpath']

    @property
    def record_path(self) -> str:
        return self.result_in_json['a01.reserved.taskrecordpath']

    @property
    def settings_in_json(self) -> dict:
        if not hasattr(self, '_settings'):
            setattr(self, '_settings', json.loads(self.settings))

        return getattr(self, '_settings')

    @property
    def result_in_json(self) -> dict:
        if not hasattr(self, '_result'):
            setattr(self, '_result', json.loads(self.result_details))

        return getattr(self, '_result')

    @property
    def category(self):
        """The category of this task. The logic is hardcoded for now. In the future, the categorizing logic will become
        configurable"""
        if not self.identifier.startswith('azure.cli'):
            return ''

        if self.identifier.startswith('azure.cli.command_modules'):
            return self.identifier.split('.')[3]
        return 'core'

    @property
    def short_name(self):
        """The category of this task. The logic is hardcoded for now. In the future, the categorizing logic will become
        configurable"""
        if not self.identifier.startswith('azure.cli'):
            return ''

        if self.identifier.startswith('azure.cli.command_modules'):
            return '.'.join(self.identifier.split('.')[6:])
        return '.'.join(self.identifier.split('.')[5:])
