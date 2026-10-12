"""create company user association

Revision ID: b45700b42f1a
Revises: 762e6d491d50
Create Date: 2025-07-30 07:41:22.156527

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b45700b42f1a"
down_revision: Union[str, Sequence[str], None] = "762e6d491d50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_company_association",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "company_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column("company_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        op.f("users_company_id_fkey"), "users", "companies", ["company_id"], ["id"]
    )
    op.drop_table("user_company_association")
