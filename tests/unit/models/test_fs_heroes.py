from forgesteel_warehouse import db
from forgesteel_warehouse.models import FsHero, User


def test_hero_basic_data_storage(test_user):
    data = FsHero(test_user, {"id": "test_hero1", "foo": "bar"})
    db.session.add(data)
    db.session.commit()

    user = User.query.filter_by(id=test_user.id).one()
    assert user.heroes is not None
    assert user.heroes is not None
    assert len(user.heroes) == 1
    assert user.heroes[0].data["foo"] == "bar"

    hero = FsHero.query.filter_by(id="test_hero1").one()
    assert hero is not None
    assert hero.data["foo"] == "bar"

def test_hero_id_parsing(test_user):
    data = FsHero(test_user, {"id": "2a", "name": "Foo Bar"})
    db.session.add(data)
    db.session.commit()

    hero = FsHero.query.filter_by(id="2a").one()
    assert hero is not None
    assert hero.data["name"] == "Foo Bar"
