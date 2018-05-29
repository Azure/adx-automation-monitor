import json
from ._share import db


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
    # connection string. Those value should be sent to the test droid through Kubernetes secret. And the values in the
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
        return self.details_in_json.get('a01.reserved.product', 'N/A')

    @property
    def remark(self):
        return self.settings_in_json.get('a01.reserved.remark', 'N/A')

    @property
    def image(self):
        return self.settings_in_json['a01.reserved.imagename']
