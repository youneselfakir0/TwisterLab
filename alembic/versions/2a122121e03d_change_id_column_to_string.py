"""change_id_column_to_string

Revision ID: 2a122121e03d
Revises: cf4ce1e9e784
Create Date: 2025-10-28 20:18:24.758877

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a122121e03d"
down_revision: Union[str, Sequence[str], None] = "cf4ce1e9e784"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change id column from Integer to String(36) for UUID support
    # First drop the primary key constraint
    op.drop_constraint("sops_pkey", "sops", type_="primary")
    # Change column type
    op.alter_column("sops", "id", type_=sa.String(36), existing_type=sa.Integer(), nullable=False)
    # Recreate primary key constraint
    op.create_primary_key("sops_pkey", "sops", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Change id column back from String to Integer
    # First drop the primary key constraint
    op.drop_constraint("sops_pkey", "sops", type_="primary")
    # Change column type back
    op.alter_column(
        "sops",
        "id",
        type_=sa.Integer(),
        existing_type=sa.String(36),
        nullable=False,
        autoincrement=True,
    )
    # Recreate primary key constraint
    op.create_primary_key("sops_pkey", "sops", ["id"])
