# pylint: disable=unused-import, too-few-public-methods, unsubscriptable-object

import json

from flask_sqlalchemy import SQLAlchemy

from .user import User

db = SQLAlchemy()  # pylint: disable=invalid-name


class Run(db.Model):
    # unique id
    id = db.Column(db.Integer, primary_key=True)

    # display name for the test run
    name = db.Column(db.String)

    # the owner who creates this run. it is the user id for a human and service principal name for a service principal
    # this column was added in later version, for legacy data, the a01.reserved.creator or creator in the settings or
    # details column will be copied here.
    owner = db.Column(db.String)

    # The test run settings is a immutable value. It is expected to be a JSON, however, it can be in any other form as
    # long as it can be represented in a string. The settings must not contain any secrets such as password or database
    # connection string. Those value should be sent to the test droid through Kubernete secret. And the values in the
    # settings can help the test droid locating to the correct secret value.
    settings = db.Column(db.String)

    # The details of the test run is mutable. It is expected to be a value bag allows the test system to store
    # information for analysis and presentation. The exact meaning and form of the value is decided by the application.
    # By default it is treated as a JSON object.
    details = db.Column(db.String)

    # The creation time of the run
    creation = db.Column(db.DateTime)

    # The status of this run. It defines the stage of execution. It includes: Initialized, Scheduling, Running, and
    # Completed.
    status = db.Column(db.String)

    @property
    def settings_in_json(self) -> dict:
        if not hasattr(self, '_settings'):
            setattr(self, '_settings', json.loads(self.settings))

        return getattr(self, '_settings')

    @property
    def details_in_json(self) -> dict:
        if not hasattr(self, '_details'):
            setattr(self, '_details', json.loads(self.details))

        return getattr(self, '_details')

    @property
    def product(self):
        return self.details_in_json['a01.reserved.product']

    @property
    def remark(self):
        return self.settings_in_json['a01.reserved.remark']

    @property
    def image(self):
        return self.settings_in_json['a01.reserved.imagename']


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
        return self.settings_in_json['classifier']['identifier']

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
