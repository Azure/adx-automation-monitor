from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id: str, user_name: str):
        self.id = user_id  # pylint: disable=invalid-name
        self.user_name = user_name
