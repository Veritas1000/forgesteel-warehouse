from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHomebrew, User

def test_homebrew_basic_data_storage(test_user):
    data = FsHomebrew(test_user, [{"foo": "bar"}])
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.homebrew is not None
    assert user.homebrew.data is not None
    assert len(user.homebrew.data) == 1
    assert user.homebrew.data[0]['foo'] == 'bar'

    homebrew = FsHomebrew.query.filter_by(user=test_user).one()
    assert homebrew is not None
    assert len(homebrew.data) == 1
    assert homebrew.data[0]['foo'] == 'bar'
