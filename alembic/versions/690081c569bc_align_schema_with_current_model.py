"""align_schema_with_current_model

Revision ID: 690081c569bc
Revises: 2a122121e03d
Create Date: 2025-10-28 20:20:08.060738

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "690081c569bc"
down_revision: Union[str, Sequence[str], None] = "2a122121e03d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove obsolete columns
    op.drop_index("ix_sops_category_priority", table_name="sops")
    op.drop_column("sops", "priority")
    op.drop_column("sops", "estimated_duration")
    op.drop_column("sops", "prerequisites")
    op.drop_column("sops", "tools_required")
    op.drop_column("sops", "common_issues")
    op.drop_column("sops", "solutions")
    op.drop_column("sops", "tags")
    op.drop_column("sops", "updated_by")
    op.drop_column("sops", "execution_count")
    op.drop_column("sops", "success_rate")
    op.drop_column("sops", "average_execution_time")
    op.drop_column("sops", "extra_metadata")

    # Adjust column types to match current model
    op.alter_column(
        "sops", "title", type_=sa.String(200), existing_type=sa.String(255), nullable=False
    )
    op.alter_column(
        "sops", "category", type_=sa.String(50), existing_type=sa.String(100), nullable=False
    )
    op.alter_column("sops", "description", nullable=False)
    op.alter_column(
        "sops", "created_by", type_=sa.String(100), existing_type=sa.String(255), nullable=False
    )
    op.alter_column(
        "sops",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        nullable=False,
    )
    op.alter_column(
        "sops",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the removed columns
    op.add_column("sops", sa.Column("extra_metadata", sa.JSON(), nullable=True))
    op.add_column("sops", sa.Column("average_execution_time", sa.Integer(), nullable=True))
    op.add_column("sops", sa.Column("success_rate", sa.Integer(), nullable=False, default=100))
    op.add_column("sops", sa.Column("execution_count", sa.Integer(), nullable=False, default=0))
    op.add_column("sops", sa.Column("updated_by", sa.String(length=255), nullable=True))
    op.add_column("sops", sa.Column("tags", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("sops", sa.Column("solutions", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("sops", sa.Column("common_issues", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("sops", sa.Column("tools_required", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("sops", sa.Column("prerequisites", sa.ARRAY(sa.String()), nullable=True))
    op.add_column("sops", sa.Column("estimated_duration", sa.Integer(), nullable=True))
    op.add_column("sops", sa.Column("priority", sa.String(length=20), nullable=False))

    # Recreate the index
    op.create_index("ix_sops_category_priority", "sops", ["category", "priority"])

    # Revert column type changes
    op.alter_column(
        "sops",
        "updated_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "sops",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "sops", "created_by", type_=sa.String(255), existing_type=sa.String(100), nullable=True
    )
    op.alter_column("sops", "description", nullable=True)
    op.alter_column(
        "sops", "category", type_=sa.String(100), existing_type=sa.String(50), nullable=False
    )
    op.alter_column(
        "sops", "title", type_=sa.String(255), existing_type=sa.String(200), nullable=False
    )
