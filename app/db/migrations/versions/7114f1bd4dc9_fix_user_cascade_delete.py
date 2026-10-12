"""empty message

Revision ID: 7114f1bd4dc9
Revises: 8e6977d2e2f9
Create Date: 2025-08-23 13:50:10.732550

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7114f1bd4dc9"
down_revision: Union[str, Sequence[str], None] = "8e6977d2e2f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("companies_owner_id_fkey"), "companies", type_="foreignkey")
    op.create_foreign_key(
        None, "companies", "users", ["owner_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "companies", type_="foreignkey")
    op.create_foreign_key(
        op.f("companies_owner_id_fkey"), "companies", "users", ["owner_id"], ["id"]
    )
