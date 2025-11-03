from forgesteel_warehouse.models import User
from forgesteel_warehouse import db

def test_user_creation_auto_auth_key():
    new_user = User(name='test_auto_auth_key')
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(name='test_auto_auth_key').one()
    assert user.auth_key is not None

def test_user_creation_set_auth_key():
    auth_key = 'TEST-ABCD-XYZ'
    new_user = User(name='test_set_auth_key', auth_key=auth_key)
    db.session.add(new_user)
    db.session.commit()

    user = User.find_by_auth_key(auth_key)
    assert user is not None
    assert user.name == 'test_set_auth_key'
