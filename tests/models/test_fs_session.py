from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsSession, User

def test_session_basic_data_storage(test_user):
    data = FsSession(test_user, [{"foo": "bar"}])
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.session is not None
    assert user.session.data is not None
    assert len(user.session.data) == 1
    assert user.session.data[0]['foo'] == 'bar'

    session = FsSession.query.filter_by(user=test_user).one()
    assert session is not None
    assert len(session.data) == 1
    assert session.data[0]['foo'] == 'bar'
