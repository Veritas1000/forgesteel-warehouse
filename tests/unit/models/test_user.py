from forgesteel_warehouse.models import User
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse import db

def test_user_creation_no_key(app):
    new_user = User(name='test_no_key')
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(name='test_no_key').one()
    assert user.auth_key is None

def test_user_creation_set_auth_key(app):
    auth_key = 'TEST-ABCD-XYZ'
    new_user = User(name='test_set_auth_key', auth_key=auth_key)
    db.session.add(new_user)
    db.session.commit()
    uid = new_user.id

    api_key = ApiKey.makeApiKey(uid, auth_key)

    user = User.find_by_api_token(api_key)
    assert user is not None
    assert user.name == 'test_set_auth_key'

def test_check_auth_key_when_no_key():
    user = User(name='test_no_key')

    assert user.check_auth_key(None) == False
