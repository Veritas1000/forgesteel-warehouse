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

migration = load_migration_as_module("c654454d655d_split_out_homebrew_arrays.py")
rev_base: str = migration.down_revision
rev_head: str = migration.revision

brew1_1 = {"id": "brew1-1", "foo": "bar"}
brew1_2 = {"id": "brew1-2", "qwer": "asdf"}
brew1_dup = {"id": "brew_duplicate_id", "name": "user 1 homebrew"}
brew2_1 = {"id": "brew2-1", "ljsdh": "saijfd"}
brew2_2 = {"id": "brew2-2", "203487j": "12-394", "ruisgh": "vjhf"}
brew2_3 = {"id": "brew2-3", "2pij34": "2p-394u"}
brew2_dup = {"id": "brew_duplicate_id", "name": "user 2 homebrew"}

initial_data = [
    {"id": 1, "name": "user1", "homebrew": [brew1_1, brew1_2, brew1_dup]},
    {"id": 2, "name": "user2", "homebrew": [brew2_1, brew2_2, brew2_3, brew2_dup]},
]


def on_init(db):
    """
    Create the initial data before migration is performed
    """
    db.reflect()
    user_table = db.metadata.tables["user"]
    homebrew_table = db.metadata.tables["fs_homebrew"]

    with db.session.connection() as conn:
        for user_data in initial_data:
            statement = insert(user_table).values(
                {"id": user_data["id"], "name": user_data["name"]}
            )
            conn.execute(statement)

            statement = insert(homebrew_table).values(
                {
                    "id": user_data["id"],
                    "user_id": user_data["id"],
                    "data": user_data["homebrew"],
                }
            )
            conn.execute(statement)

        db.session.commit()


def on_upgrade(db):
    """
    Ensure that data was successfully migrated
    """
    db.reflect()
    homebrew_table = db.metadata.tables["fs_homebrew"]

    with db.session.connection() as conn:
        request = select(homebrew_table.c.id, homebrew_table.c.user_id, homebrew_table.c.data)

        actual = {
            homebrew[0]: {"user_id": homebrew[1], "data": homebrew[2]}
            for homebrew in conn.execute(request).fetchall()
        }  ## { homebrew_id: {user_id, data} }

        assert len(actual.keys()) == 7
        assert 1 not in actual
        assert 2 not in actual

        assert "brew1-1" in actual
        assert actual["brew1-1"]["user_id"] == 1
        assert actual["brew1-1"]["data"] == brew1_1

        assert "brew1-2" in actual
        assert actual["brew1-2"]["user_id"] == 1
        assert actual["brew1-2"]["data"] == brew1_2

        other_user1_brew = list(
            filter(
                lambda brew: brew["user_id"] == 1
                and brew["data"]["id"].startswith("brew_duplicate_id"),
                actual.values(),
            )
        )
        assert other_user1_brew is not None
        assert len(other_user1_brew) == 1
        assert other_user1_brew[0]["data"] == brew1_dup

        assert "brew2-1" in actual
        assert actual["brew2-1"]["user_id"] == 2
        assert actual["brew2-1"]["data"] == brew2_1

        assert "brew2-2" in actual
        assert actual["brew2-2"]["user_id"] == 2
        assert actual["brew2-2"]["data"] == brew2_2

        assert "brew2-3" in actual
        assert actual["brew2-3"]["user_id"] == 2
        assert actual["brew2-3"]["data"] == brew2_3

        other_user2_brew = list(
            filter(
                lambda brew: brew["user_id"] == 2
                and brew["data"]["id"].startswith("brew_duplicate_id"),
                actual.values(),
            )
        )
        assert other_user2_brew is not None
        assert len(other_user2_brew) == 1
        assert other_user2_brew[0]["data"] == brew2_dup


def on_downgrade(db):
    """
    Ensure that data was successfully migrated
    """
    db.reflect()
    homebrew_table = db.metadata.tables["fs_homebrew"]

    with db.engine.connect() as conn:
        request = select(homebrew_table.c.user_id, homebrew_table.c.data)

        actual = {
            homebrew[0]: homebrew[1]
            for homebrew in conn.execute(request).fetchall()
        } ## { user_id: homebrew }

        for user in initial_data:
            assert user["id"] in actual
            assert user["homebrew"] == actual[user["id"]]
