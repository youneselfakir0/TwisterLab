"""add_priority_field_to_sops

Revision ID: 0a7c79ca3fd5
Revises: 690081c569bc
Create Date: 2025-10-28 20:25:15.732105

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0a7c79ca3fd5"
down_revision: Union[str, Sequence[str], None] = "690081c569bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add priority column to sops table
    op.add_column(
        "sops", sa.Column("priority", sa.String(length=20), nullable=False, server_default="medium")
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove priority column from sops table
    op.drop_column("sops", "priority")
