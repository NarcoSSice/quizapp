"""add quiz result model

Revision ID: 29536ba46e3d
Revises: 601e3a3b4701
Create Date: 2025-08-14 20:10:39.473180

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "29536ba46e3d"
down_revision: Union[str, Sequence[str], None] = "601e3a3b4701"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "quiz_results",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("answered_questions", sa.Integer(), nullable=False),
        sa.Column("correct_answers", sa.Integer(), nullable=False),
        sa.Column(
            "last_attempt_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "company_id", "quiz_id"),
    )
    op.drop_constraint(
        op.f("company_actions_company_id_fkey"), "company_actions", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "company_actions", "companies", ["company_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "company_actions", type_="foreignkey")
    op.create_foreign_key(
        op.f("company_actions_company_id_fkey"),
        "company_actions",
        "companies",
        ["company_id"],
        ["id"],
    )
    op.drop_table("quiz_results")
