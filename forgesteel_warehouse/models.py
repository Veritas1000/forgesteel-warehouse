import logging
from argon2 import PasswordHasher

from forgesteel_warehouse import db, jwt
from forgesteel_warehouse.api_key import ApiKey

log = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'user'

    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String(100))
    auth_key = db.mapped_column(db.String(80))
    
    heroes = db.relationship('FsHeroes', uselist=False, back_populates='user')
    homebrew = db.relationship('FsHomebrew', uselist=False, back_populates='user')

    def __init__(self, name, auth_key=None):
        self.name = name
        self.auth_key = None
        if auth_key is not None:
            ph = PasswordHasher()
            hashed = ph.hash(auth_key)
            self.auth_key = hashed

    def get_api_token(self):
        if self.auth_key is not None:
            return ApiKey.makeApiKey(self.id, self.auth_key)
        else:
            return None

    def check_auth_key(self, auth_key):
        if self.auth_key is None:
            return False
        ph = PasswordHasher()
        return ph.verify(self.auth_key, auth_key)

    @classmethod
    def find_by_api_token(cls, api_token):
        (uid, key) = ApiKey.parseApiKey(api_token)
        user = db.session.execute(db.select(User).filter_by(id=uid)).scalar_one_or_none()
        
        if user is not None and user.check_auth_key(key):
            return user
    
        return None

    def __str__(self):
        return f"[User {self.id} name={self.name} auth_key={self.auth_key}]"

    def __repr__(self):
        return self.__str__()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = int(jwt_data["sub"])
    return User.query.filter_by(id=identity).one_or_none()

class FsHeroes(db.Model):
    __tablename__ = 'fs_heroes'
    
    id = db.mapped_column(db.Integer, primary_key=True)
    user_id = db.mapped_column(db.ForeignKey('user.id'), unique=True, nullable=True)
    user = db.relationship('User', back_populates='heroes')

    data = db.mapped_column(db.JSON)

    def __init__(self, user, data):
        self.user = user
        self.data = data

class FsHomebrew(db.Model):
    __tablename__ = 'fs_homebrew'
    
    id = db.mapped_column(db.Integer, primary_key=True)
    user_id = db.mapped_column(db.ForeignKey('user.id'), unique=True, nullable=True)
    user = db.relationship('User', back_populates='homebrew')

    data = db.mapped_column(db.JSON)

    def __init__(self, user, data):
        self.user = user
        self.data = data
