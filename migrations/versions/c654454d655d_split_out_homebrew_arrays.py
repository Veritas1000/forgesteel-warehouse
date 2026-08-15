"""Split out homebrew arrays

Revision ID: c654454d655d
Revises: 5dba7c4db2c5
Create Date: 2026-08-14 09:19:35.697796

"""
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c654454d655d'
down_revision = '5dba7c4db2c5'
branch_labels = None
depends_on = None


def upgrade():
    ## Split the single array per user
    conn = op.get_bind()
    res = conn.execute(sa.text("select id, user_id, data from fs_homebrew"))
    results = res.fetchall()
    homebrews = []
    prev_brew_ids = []
    for user_homebrews in results:
        prev_brew_ids.append(user_homebrews[0])
        user_id = user_homebrews[1]

        if isinstance(user_homebrews[2], str):
            homebrew_data = json.loads(user_homebrews[2])
        else:
            homebrew_data = user_homebrews[2]

        for n, brew_data in enumerate(homebrew_data):
            brew_id = (
                brew_data["id"] if "id" in brew_data else f"{user_id}-generated-{n}"
            )
            homebrews.append({"id": brew_id, "user_id": user_id, "data": brew_data})

    ## drop the old table
    op.drop_table("fs_homebrew")

    ## recreate the table
    fs_homebrew = op.create_table(
        "fs_homebrew",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    ## insert the split records
    op.bulk_insert(fs_homebrew, homebrews)


def downgrade():
    ## Re-merge the homebrews into a single array per user
    conn = op.get_bind()
    res = conn.execute(sa.text("select user_id, data from fs_homebrew"))
    results = res.fetchall()
    homebrew_per_user = {}
    for user_homebrew in results:
        user_id = user_homebrew[0]

        if isinstance(user_homebrew[1], str):
            brew_data = json.loads(user_homebrew[1])
        else:
            brew_data = user_homebrew[1]

        if user_id not in homebrew_per_user:
            homebrew_per_user[user_id] = []

        homebrew_per_user[user_id].append(brew_data)

    rows = [{"user_id": u, "data": d} for u, d in homebrew_per_user.items()]

    ## drop the old table
    op.drop_table("fs_homebrew")

    ## recreate the table
    fs_homebrew = op.create_table(
        "fs_homebrew",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="user_id_unique"),
    )
    ## insert the joined records
    op.bulk_insert(fs_homebrew, rows)
