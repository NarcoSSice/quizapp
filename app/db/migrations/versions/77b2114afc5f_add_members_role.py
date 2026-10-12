"""add members role

Revision ID: 77b2114afc5f
Revises: b45700b42f1a
Create Date: 2025-07-30 17:36:04.414163

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "77b2114afc5f"
down_revision: Union[str, Sequence[str], None] = "b45700b42f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roletype = postgresql.ENUM("owner", "admin", "member", name="roletype", create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    roletype.create(op.get_bind())

    op.add_column(
        "user_company_association",
        sa.Column("role", roletype, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user_company_association", "role")

    roletype.drop(op.get_bind())
