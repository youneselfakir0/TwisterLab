"""add_applicable_issues_column

Revision ID: cf4ce1e9e784
Revises: 2dc2e31027ab
Create Date: 2025-10-28 20:13:05.136235

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf4ce1e9e784"
down_revision: Union[str, Sequence[str], None] = "2dc2e31027ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""add_applicable_issues_column

Revision ID: cf4ce1e9e784
Revises: 2dc2e31027ab
Create Date: 2025-10-28 20:13:05.136235

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf4ce1e9e784"
down_revision: Union[str, Sequence[str], None] = "2dc2e31027ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add applicable_issues column to sops table
    op.add_column(
        "sops", sa.Column("applicable_issues", sa.ARRAY(sa.String()), nullable=False, default=[])
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove applicable_issues column from sops table
    op.drop_column("sops", "applicable_issues")
