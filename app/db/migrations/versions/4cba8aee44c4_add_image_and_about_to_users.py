"""add image and about to users

Revision ID: 4cba8aee44c4
Revises: e43f557920ed
Create Date: 2025-07-28 11:24:15.052554

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4cba8aee44c4"
down_revision: Union[str, Sequence[str], None] = "e43f557920ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("about", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("image_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "image_url")
    op.drop_column("users", "about")
