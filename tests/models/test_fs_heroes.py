from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHeroes, User

def test_basic_data_storage(test_user):
    data = FsHeroes(test_user, [{"foo": "bar"}])
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.heroes is not None
    assert user.heroes.data is not None
    assert len(user.heroes.data) == 1
    assert user.heroes.data[0]['foo'] == 'bar'

    heroes = FsHeroes.query.filter_by(user=test_user).one()
    assert heroes is not None
    assert len(heroes.data) == 1
    assert heroes.data[0]['foo'] == 'bar'
