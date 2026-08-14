from collections import defaultdict, namedtuple
from typing import Callable, List

import pytest
from alembic.command import downgrade, upgrade

from forgesteel_warehouse import db
from tests.unit.database.data_migrations import (
    migration_5dba7c4db2c5,
    migration_c654454d655d,
)


def get_data_migrations():
    """
    Returns tests for data migrations, from tests/data_migrations folder.
    """

    return make_validation_params_groups(
        migration_5dba7c4db2c5,
        migration_c654454d655d,
    )


# Represents test for 'data' migration.
# Contains revision to be tested, it's previous revision, and callbacks that
# could be used to perform validation.
MigrationValidationParamsGroup = namedtuple(
    "MigrationData", ["rev_base", "rev_head", "on_init", "on_upgrade", "on_downgrade"]
)


def make_validation_params_groups(*migrations) -> List[MigrationValidationParamsGroup]:
    """
    Creates objects that describe test for data migrations.
    See examples in tests/data_migrations/migration_*.py.
    """
    data = []
    for migration in migrations:

        # Ensure migration has all required params
        for required_param in ["rev_base", "rev_head"]:
            if not hasattr(migration, required_param):
                raise RuntimeError(
                    "{param} not specified for {migration}".format(
                        param=required_param, migration=migration.__name__
                    )
                )

        # Set up callbacks
        callbacks = defaultdict(lambda: lambda *args, **kwargs: None)
        for callback in ["on_init", "on_upgrade", "on_downgrade"]:
            if hasattr(migration, callback):
                callbacks[callback] = getattr(migration, callback)

        data.append(
            MigrationValidationParamsGroup(
                rev_base=migration.rev_base,
                rev_head=migration.rev_head,
                on_init=callbacks["on_init"],
                on_upgrade=callbacks["on_upgrade"],
                on_downgrade=callbacks["on_downgrade"],
            )
        )

    return data


@pytest.mark.parametrize(
    ("rev_base", "rev_head", "on_init", "on_upgrade", "on_downgrade"),
    get_data_migrations(),
)
def test_data_migrations(
    alembic_config,
    rev_base: str,
    rev_head: str,
    on_init: Callable,
    on_upgrade: Callable,
    on_downgrade: Callable,
):
    # Upgrade to previous migration before target and add some data,
    # that would be changed by tested migration.
    upgrade(alembic_config, rev_base)
    on_init(db)

    # Perform upgrade in tested migration.
    # Check that data is migrated correctly in on_upgrade callback
    upgrade(alembic_config, rev_head)
    on_upgrade(db)

    # Perform downgrade in tested migration.
    # Check that changes are reverted back using on_downgrade callback
    downgrade(alembic_config, rev_base)
    on_downgrade(db)
