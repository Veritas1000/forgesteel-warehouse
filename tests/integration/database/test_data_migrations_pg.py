from typing import Callable

import pytest
from alembic.command import downgrade, upgrade

from forgesteel_warehouse import db
from tests.unit.database.test_data_migrations import get_data_migrations


@pytest.mark.parametrize(
    ("rev_base", "rev_head", "on_init", "on_upgrade", "on_downgrade"),
    get_data_migrations(),
)
def test_data_migrations_pg(
    alembic_pg_config,
    rev_base: str,
    rev_head: str,
    on_init: Callable,
    on_upgrade: Callable,
    on_downgrade: Callable,
):
    # Upgrade to previous migration before target and add some data,
    # that would be changed by tested migration.
    upgrade(alembic_pg_config, rev_base)
    on_init(db)

    # Perform upgrade in tested migration.
    # Check that data is migrated correctly in on_upgrade callback
    upgrade(alembic_pg_config, rev_head)
    on_upgrade(db)

    # Perform downgrade in tested migration.
    # Check that changes are reverted back using on_downgrade callback
    downgrade(alembic_pg_config, rev_base)
    on_downgrade(db)
