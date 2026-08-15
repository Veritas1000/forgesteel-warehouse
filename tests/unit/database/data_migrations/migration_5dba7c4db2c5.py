# Load migration as module
import importlib
import os
import sys
from pathlib import Path

from sqlalchemy import insert, select

PROJECT_PATH = Path(__file__).parent.parent.parent.parent.parent.resolve()
def load_migration_as_module(file: str):
    """
    Allows to import alembic migration as a module.
    """
    spec = importlib.util.spec_from_file_location(  # type: ignore
        file, os.path.join(PROJECT_PATH, "migrations", "versions", file)
    )
    module = importlib.util.module_from_spec(spec) # type: ignore
    sys.modules[file] = module

    spec.loader.exec_module(module)
    return module

migration = load_migration_as_module("5dba7c4db2c5_create_new_hero_table.py")
rev_base: str = migration.down_revision
rev_head: str = migration.revision

hero1_1 = {"id": "hero1-1", "foo": "bar"}
hero1_2 = {"id": "hero1-2", "qwer": "asdf"}
hero1_dup = {"id": "hero_duplicate_id", "name": "user 1 hero"}
hero2_1 = {"id": "hero2-1", "ljsdh": "saijfd"}
hero2_2 = {"id": "hero2-2", "203487j": "12-394", "ruisgh": "vjhf"}
hero2_3 = {"id": "hero2-3", "2pij34": "2p-394u"}
hero2_dup = {"id": "hero_duplicate_id", "name": "user 2 hero"}

initial_data = [
    {"id": 1, "name": "user1", "heroes": [hero1_1, hero1_2, hero1_dup]},
    {"id": 2, "name": "user2", "heroes": [hero2_1, hero2_2, hero2_3, hero2_dup]},
]


def on_init(db):
    """
    Create the initial data before migration is performed
    """
    db.reflect()
    user_table = db.metadata.tables["user"]
    heroes_table = db.metadata.tables["fs_heroes"]

    hId = 1
    with db.session.connection() as conn:
        for user_data in initial_data:
            statement = insert(user_table).values(
                {"id": user_data["id"], "name": user_data["name"]}
            )
            conn.execute(statement)

            statement = insert(heroes_table).values(
                {"id": hId, "user_id": user_data["id"], "data": user_data["heroes"]}
            )
            conn.execute(statement)

            hId += 1

        db.session.commit()


def on_upgrade(db):
    """
    Ensure that data was successfully migrated
    """
    db.reflect()
    hero_table = db.metadata.tables["fs_hero"]

    with db.session.connection() as conn:
        request = select(hero_table.c.id, hero_table.c.user_id, hero_table.c.data)

        actual = {
            hero[0]: {"user_id": hero[1], "data": hero[2]}
            for hero in conn.execute(request).fetchall()
        }  ## { hero_id: {user_id, data} }

        assert len(actual) == 7

        assert "hero1-1" in actual
        assert actual["hero1-1"]["user_id"] == 1
        assert actual["hero1-1"]["data"] == hero1_1

        assert "hero1-2" in actual
        assert actual["hero1-2"]["user_id"] == 1
        assert actual["hero1-2"]["data"] == hero1_2

        other_user1_hero = list(filter(
            lambda hero: hero["user_id"] == 1
            and hero["data"]["id"].startswith("hero_duplicate_id"),
            actual.values(),
        ))
        assert other_user1_hero is not None
        assert len(other_user1_hero) == 1
        assert other_user1_hero[0]["data"] == hero1_dup

        assert "hero2-1" in actual
        assert actual["hero2-1"]["user_id"] == 2
        assert actual["hero2-1"]["data"] == hero2_1

        assert "hero2-2" in actual
        assert actual["hero2-2"]["user_id"] == 2
        assert actual["hero2-2"]["data"] == hero2_2

        assert "hero2-3" in actual
        assert actual["hero2-3"]["user_id"] == 2
        assert actual["hero2-3"]["data"] == hero2_3

        other_user2_hero = list(
            filter(
                lambda hero: hero["user_id"] == 2
                and hero["data"]["id"].startswith("hero_duplicate_id"),
                actual.values(),
            )
        )
        assert other_user2_hero is not None
        assert len(other_user2_hero) == 1
        assert other_user2_hero[0]["data"] == hero2_dup


def on_downgrade(db):
    """
    Ensure that data was successfully migrated
    """
    db.reflect()
    heroes_table = db.metadata.tables["fs_heroes"]

    with db.engine.connect() as conn:
        request = select(heroes_table.c.user_id, heroes_table.c.data)

        actual = {
            heroes[0]: heroes[1]
            for heroes in conn.execute(request).fetchall()
        } ## { user_id: heroes }

        for user in initial_data:
            assert user["id"] in actual
            assert user["heroes"] == actual[user["id"]]
