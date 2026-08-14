"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.

Does not require any maintenance - you just add it once to check 80% of typos
and mistakes in migrations forever.
"""


import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import Script, ScriptDirectory


def get_revisions():
    config = Config()
    config.set_main_option("script_location", "migrations")

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions

@pytest.mark.parametrize("revision", get_revisions())
def test_migrations_stairway2(alembic_config, revision: Script):
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_config, revision.down_revision or "-1")  # type: ignore
    upgrade(alembic_config, revision.revision)
