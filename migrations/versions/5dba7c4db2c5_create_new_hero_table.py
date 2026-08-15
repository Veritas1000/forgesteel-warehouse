"""Create new Hero table

Revision ID: 5dba7c4db2c5
Revises: 5eafd5183cba
Create Date: 2026-04-19 10:21:41.451026

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5dba7c4db2c5'
down_revision = '5eafd5183cba'
branch_labels = None
depends_on = None

def upgrade():
    ## Create the new table
    fs_hero = op.create_table('fs_hero',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('id')
    )

    ## Copy over all existing heroes into the new table
    ## splitting the single array per user
    conn = op.get_bind()
    res = conn.execute(sa.text("select user_id, data from fs_heroes"))
    results = res.fetchall()
    heroes = []
    all_hero_ids = []
    for user_heroes in results:
        user_id = user_heroes[0]

        if isinstance(user_heroes[1], str):
            heroes_data = json.loads(user_heroes[1])
        else:
            heroes_data = user_heroes[1]

        for n, hero_data in enumerate(heroes_data):
            hero_id = hero_data["id"] if "id" in hero_data else f"{user_id}-generated-{n}"
            hero_id = f"{hero_id}-{user_id}-{n}" if hero_id in all_hero_ids else hero_id
            heroes.append({
                "id": hero_id,
                "user_id": user_id,
                "data": hero_data
            })
            all_hero_ids.append(hero_id)

    op.bulk_insert(fs_hero, heroes)

    ## Drop the old data
    op.drop_table("fs_heroes")


def downgrade():
    ## Recreate the old table
    fs_heroes = op.create_table(
        "fs_heroes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    ## Re-merge the heroes into a single array per user
    conn = op.get_bind()
    res = conn.execute(sa.text("select user_id, data from fs_hero"))
    results = res.fetchall()
    heroes_per_user = {}
    for user_heroes in results:
        user_id = user_heroes[0]

        if isinstance(user_heroes[1], str):
            hero_data = json.loads(user_heroes[1])
        else:
            hero_data = user_heroes[1]

        if user_id not in heroes_per_user:
            heroes_per_user[user_id] = []

        heroes_per_user[user_id].append(hero_data)

    rows = [{"user_id": u, "data": d} for u,d in heroes_per_user.items()]

    op.bulk_insert(fs_heroes, rows)

    ## Drop the new table
    op.drop_table('fs_hero')
