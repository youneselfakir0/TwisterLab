"""Create agents table

Revision ID: 0001_create_agents
Revises:
Create Date: 2025-11-25 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op  # type: ignore

revision = "0001_create_agents"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("agents")
