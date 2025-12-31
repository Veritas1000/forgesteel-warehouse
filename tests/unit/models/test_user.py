from forgesteel_warehouse.models import User
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse import db

def test_user_creation_no_key(app):
    new_user = User(name='test_no_key')
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(name='test_no_key').one()
    assert user._auth_key is None

def test_user_creation_sets_auth_key(app):
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

def test_check_auth_key_wrong_key():
    auth_key = 'TEST-ABCD-XYZ'
    user = User(name='test_set_auth_key', auth_key=auth_key)

    assert user.check_auth_key('WRONG_KEY') is False

def test_set_auth_key(app):
    auth_key1 = 'TEST-ABCD-XYZ'
    user = User(name='test_set_auth_key', auth_key=auth_key1)
    db.session.add(user)
    db.session.commit()
    uid = user.id

    token1 = ApiKey.makeApiKey(uid, auth_key1)
    assert token1 != auth_key1
    assert user.check_auth_key(auth_key1) is True

    auth_key2 = 'TEST2-1234-9876'
    user.set_auth_key(auth_key2)
    db.session.commit()
    token2 = ApiKey.makeApiKey(uid, auth_key2)

    assert token2 != token1
    assert user.check_auth_key(auth_key1) is False
    assert user.check_auth_key(auth_key2) is True

def test_user_find_by_patreon_id(app):
    id1 = '12345'
    new_user1 = User(name='test_patreon_1', patreon_id=id1)
    new_user1.patreon_email = 'test1@email.com'
    db.session.add(new_user1)

    new_user2 = User(name='test_patreon_2', patreon_id='32145')
    new_user2.patreon_email = 'test2@email.com'
    db.session.add(new_user2)

    db.session.commit()

    user = User.find_by_patreon_id(id1)
    assert user is not None
    assert user.name == 'test_patreon_1'
