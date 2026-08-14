from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHomebrew, User


def test_homebrew_basic_data_storage(test_user):
    data = FsHomebrew(test_user, {"id": "brew1", "foo": "bar"})
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.homebrew is not None
    assert len(user.homebrew) == 1
    assert user.homebrew[0].data["foo"] == "bar"

    homebrew = FsHomebrew.query.filter_by(id="brew1").one()
    assert homebrew is not None
    assert homebrew.data["foo"] == "bar"
