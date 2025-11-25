from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHiddenSettings, User

def test_hidden_settings_basic_data_storage(test_user):
    data = FsHiddenSettings(test_user, ["foo", "bar", "baz"])
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.hidden_settings is not None
    assert user.hidden_settings.data is not None
    assert len(user.hidden_settings.data) == 3
    assert user.hidden_settings.data[0] == 'foo'
    assert user.hidden_settings.data[1] == 'bar'
    assert user.hidden_settings.data[2] == 'baz'

    hidden_settings = FsHiddenSettings.query.filter_by(user=test_user).one()
    assert hidden_settings is not None
    assert len(user.hidden_settings.data) == 3
    assert user.hidden_settings.data[0] == 'foo'
    assert user.hidden_settings.data[1] == 'bar'
    assert user.hidden_settings.data[2] == 'baz'
