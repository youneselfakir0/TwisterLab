"""Create SOPs table

Revision ID: 2dc2e31027ab
Revises:
Create Date: 2025-10-28 18:51:33.838041

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2dc2e31027ab"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create SOPs table
    op.create_table(
        "sops",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("estimated_duration", sa.Integer(), nullable=True),
        sa.Column("steps", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("prerequisites", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("tools_required", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("common_issues", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("solutions", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("updated_by", sa.String(length=255), nullable=True),
        sa.Column("execution_count", sa.Integer(), nullable=False, default=0),
        sa.Column("success_rate", sa.Integer(), nullable=False, default=100),
        sa.Column("average_execution_time", sa.Integer(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_sops_category_priority", "category", "priority"),
        sa.Index("ix_sops_title", "title"),
        sa.Index("ix_sops_created_at", "created_at"),
        sa.Index("ix_sops_is_active", "is_active"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop SOPs table
    op.drop_table("sops")
