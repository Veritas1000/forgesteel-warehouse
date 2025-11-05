import uuid
import logging

from . import db, jwt

log = logging.getLogger(__name__)

class User(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String(100))
    auth_key = db.mapped_column(db.String(80))

    def __init__(self, name, auth_key=None):
        self.name = name
        self.auth_key = auth_key or uuid.uuid4().hex

    @classmethod
    def find_by_auth_key(cls, auth_key):
        return cls.query.filter_by(auth_key=auth_key).one_or_none()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = int(jwt_data["sub"])
    return User.query.filter_by(id=identity).one_or_none()
